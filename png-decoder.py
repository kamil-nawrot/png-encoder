import os
import zlib
import numpy as np
import matplotlib.pyplot as plt
import png
import itertools
import array
import rsa


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class ImageFile:
    def __init__(self, filename, mode):
        self.filename = filename
        self.desc = open(self.filename, mode)
        self.fileSize = os.path.getsize(self.filename)
        self.imageProperties = {}
        self.content = None
        self.encodedContent = b""
        self.compressedContent = b""
        self.contentSize = None
        self.signature = self.desc.read(8)
        self.foundIDAT = []
        self.pixelArray = []
        self.redChannel = []
        self.greenChannel = []
        self.blueChannel = []
        self.keyPair = rsa.RSA(256)
        self.xorKey = np.random.randint(1073741823, 2147483647)

    def find_chunk(self, chunk_type, start):

        self.desc.seek(start, 0)
        while self.desc.tell() < self.fileSize:
            if self.desc.read(1).find(bytes(chunk_type[0], 'utf-8')) != -1:
                if self.desc.read(3).find(bytes(chunk_type[1:4], 'utf-8')) != -1:
                    self.desc.seek(-8, 1)
                    chunk_length = int.from_bytes(self.desc.read(4), byteorder="big")
                    # print(chunk_type, "found ( length:", str(chunk_length), ") at", str(self.desc.tell()))
                    if chunk_type == "IDAT":
                        if [self.desc.tell(), chunk_length] not in self.foundIDAT:
                            self.foundIDAT.append([self.desc.tell(), chunk_length])
                        else:
                            self.find_chunk("IDAT", self.desc.tell()+chunk_length)
                            return str(False)
                    self.desc.read(4)
                    return self.desc.tell()-4, chunk_length
        return str(False)

    def check_if_png(self):
        self.desc.seek(0, 0)
        self.signature = self.desc.read(8)
        if type(self.signature) is bytes and self.signature == b'\x89PNG\r\n\x1a\n':
            return True
        elif type(self.signature) is str and self.signature == '89504e470d0a1a0a':
            return True
        elif type(self.signature) is int and self.signature == 9894494448401390090:
            return True
        else:
            return False

    def update_properties(self):
        self.find_chunk("IHDR", 0)
        self.imageProperties["width"] = int.from_bytes(self.desc.read(4), byteorder="big")
        self.imageProperties["height"] = int.from_bytes(self.desc.read(4), byteorder="big")
        self.imageProperties["bitDepth"] = int.from_bytes(self.desc.read(1), byteorder="big")
        self.imageProperties["colorType"] = int.from_bytes(self.desc.read(1), byteorder="big")
        self.imageProperties["compressionMethod"] = int.from_bytes(self.desc.read(1), byteorder="big")
        self.imageProperties["filterMethod"] = int.from_bytes(self.desc.read(1), byteorder="big")
        self.imageProperties["interlaceMethod"] = int.from_bytes(self.desc.read(1), byteorder="big")

    def display_properties(self):
        def color_type_switch(color):
            switcher = {
                0: "1 - gray scale",
                2: "3 - true color (RGB)",
                3: "1 - indexed",
                4: "2 - gray scale with alpha",
                6: "4 - RGB with alpha"
            }
            return switcher.get(color, "invalid color type")

        print("FILE SIZE:              " + str(self.fileSize) + " bytes")
        print("IMAGE DIMENSIONS:       " + str(self.imageProperties["width"]) + "x" + str(self.imageProperties["height"]))
        print("BIT DEPTH:              " + str(self.imageProperties["bitDepth"]))
        print("COLOR TYPE:             " + color_type_switch(self.imageProperties["colorType"]))
        if self.imageProperties["compressionMethod"] == 0:
            print("COMPRESSION METHOD:     " + str(self.imageProperties["compressionMethod"]) + " - deflate")
        else:
            print("COMPRESSION METHOD:     " + str(self.imageProperties["compressionMethod"]) + " - unknown method")
        if self.imageProperties["filterMethod"] == 0:
            print("FILTER METHOD:          " + str(self.imageProperties["filterMethod"]) + " - default")
        else:
            print("FILTER METHOD:          " + str(self.imageProperties["filterMethod"]) + " - unknown method")
        if self.imageProperties["interlaceMethod"] == 0:
            print("INTERLACE METHOD:       " + str(self.imageProperties["interlaceMethod"]) + " - no interlace")
        else:
            print("INTERLACE METHOD:       " + str(self.imageProperties["interlaceMethod"]) + " - Adam7")

        chunk_size = 0
        if not self.find_chunk("iTXt", 0):
            if not self.find_chunk("tEXt", 0):
                if not self.find_chunk("zTXt", 0):
                    print("no textual data found")
                else:
                    chunk_size = self.find_chunk("zTXt", 0)
            else:
                chunk_size = self.find_chunk("tEXt", 0)
        else:
            chunk_size = self.find_chunk("iTXt", 0)

        if chunk_size > 0:
            print(self.desc.read(chunk_size).decode('utf-8'))

    def read_content(self):
        for x in range(100):
            self.find_chunk("IDAT", 0)
        for idat in self.foundIDAT:
            self.desc.seek(idat[0]+4, 0)
            self.compressedContent += self.desc.read(idat[1])
            print("reading content...")

    def decompress(self):
        decompressor = zlib.decompressobj()
        self.content = decompressor.decompress(self.compressedContent)
        decompressor.flush()
        self.contentSize = len(self.content)
        print("decompression done:", self.contentSize)

    def create_pixel_array(self):
        for index, pixel in enumerate(self.content):
            if index % (3*self.imageProperties["width"] + 1) is not 0:
                self.pixelArray.append(pixel)
        print("pixel array created")
        # self.redChannel = []
        # self.greenChannel = []
        # self.blueChannel = []
        # self.pixelArray = list(chunks(self.pixelArray, 3))
        # for pixel in self.pixelArray:
        #     self.redChannel.append(pixel[0])
        #     self.greenChannel.append(pixel[1])
        #     self.blueChannel.append(pixel[2])

    def compute_spectrum(self, color):
        spectrum = None
        if color == "red":
            spectrum = np.fft.fft(self.redChannel[:1024])
        elif color == "green":
            spectrum = np.fft.fft(self.greenChannel[:1024])
        elif color == "blue":
            spectrum = np.fft.fft(self.blueChannel[:1024])
        spectrum_amp = np.abs(spectrum)
        plt.plot(spectrum_amp)
        plt.show()

    def encode_with_rsa(self):
        filter_mask = [1] * self.contentSize
        for index, value in enumerate(filter_mask):
            if index % (3 * self.imageProperties["width"] + 1) is 0:
                filter_mask[index] = 0
        image_data = list(itertools.compress(self.content, filter_mask))
        image_data = array.array('B', image_data).tobytes()
        print(image_data)

        original_array = []
        for index, pixel in enumerate(image_data):
            original_array.append(pixel)
        original_array = list(chunks(original_array, self.imageProperties["width"]*3))

        png.from_array(original_array[:self.imageProperties["width"]][:self.imageProperties["height"]], 'RGB') \
            .save('./img/original_result.png')

        self.keyPair.generate_key_pairs()

        print("start encoding...")

        encoded_data = b""
        for x in range(0, len(image_data)+1, 32):
            encoded_bytes = image_data[x:x+32]
            length = len(encoded_bytes)
            encoded_bytes = int.from_bytes(encoded_bytes, byteorder="big")
            encoded_bytes = self.keyPair.encode(encoded_bytes).to_bytes(32, byteorder="big")
            encoded_bytes = encoded_bytes[:length]
            encoded_data += encoded_bytes

        print("ORIGINAL DATA: ", len(image_data))
        print("ENCODED DATA: ", len(encoded_data))

        encoded_array = []
        for index, pixel in enumerate(encoded_data):
            encoded_array.append(pixel)

        self.encodedContent = encoded_array[:self.imageProperties["width"]*self.imageProperties["height"]*3]
        encoded_array = list(chunks(encoded_array, self.imageProperties["width"]*3))

        print(list(chunks(self.pixelArray, self.imageProperties["width"]*3)))
        print(encoded_array)

        png.from_array(encoded_array[:self.imageProperties["width"]][:self.imageProperties["height"]], 'RGB')\
            .save('./img/result.png')

    def decode_with_rsa(self):

        encoded_array = self.encodedContent
        encoded_data = b""
        for pixel in encoded_array:
            encoded_data += pixel.to_bytes(1, byteorder="big")

        decoded_data = b""
        for x in range(0, len(encoded_data), 32):
            decoded_block = encoded_data[x:x+32]
            decoded_block = int.from_bytes(decoded_block, byteorder="big")
            decoded_block = self.keyPair.decode(decoded_block)
            decoded_data += decoded_block.to_bytes(32, byteorder="big")

        print("DECODED DATA: ", len(decoded_data))
        decoded_array = []
        for index, pixel in enumerate(decoded_data):
            decoded_array.append(pixel)
        decoded_array = list(chunks(decoded_array, self.imageProperties["width"]*3))

        print(decoded_array)

        png.from_array(decoded_array[:self.imageProperties["width"]][:self.imageProperties["height"]], 'RGB') \
            .save('./img/result-decoded.png')

        # decoded_data = b""
        # decoded_block = b""
        #
        # for x in range(1, (self.contentSize // 32) + 2):
        #     decoded_block = b""
        #     for byte in self.encodedContent[32*x:32*(x+1)]:
        #         print(byte)
        #         decoded_block += byte.to_bytes(1, byteorder="big")
        #     decoded_data += self.keyPair.decode(int.from_bytes(decoded_block, byteorder="big")).to_bytes(32, byteorder="big")
        #     print("Decoded:", decoded_data)
        #
        # print("Decoded:", decoded_data)
        #
        # decodedArray = []
        # for index, pixel in enumerate(decoded_data):
        #     decodedArray.append(pixel)
        #
        # decodedArray = list(chunks(decodedArray, self.imageProperties["width"]*3))
        # print(decodedArray)

##########################################################


originalImage = ImageFile("./img/image_cat.png", "rb")
if originalImage.check_if_png():
    originalImage.update_properties()
    originalImage.read_content()
    originalImage.decompress()
    originalImage.create_pixel_array()
    # originalImage.display_properties()
    # originalImage.compute_spectrum("red")
    # originalImage.compute_spectrum("green")
    # originalImage.compute_spectrum("blue")

    originalImage.encode_with_rsa()
    originalImage.decode_with_rsa()

else:
    print("Wrong file format")