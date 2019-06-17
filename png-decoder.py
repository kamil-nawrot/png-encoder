import os
import zlib
import numpy as np
import matplotlib.pyplot as plt
import png
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
        self.encodedContent = None
        self.compressedContent = None
        self.contentSize = None
        self.signature = self.desc.read(8)
        self.pixelArray = []
        self.redChannel = []
        self.greenChannel = []
        self.blueChannel = []
        self.keyPair = []

    def find_chunk(self, chunk_type):
        self.desc.seek(0, 0)
        while self.desc.tell() < self.fileSize:
            if self.desc.read(1).find(bytes(chunk_type[0], 'utf-8')) != -1:
                if self.desc.read(3).find(bytes(chunk_type[1:4], 'utf-8')) != -1:
                    self.desc.seek(-8, 1)
                    chunk_length = int.from_bytes(self.desc.read(4), byteorder="big")
                    print(
                        chunk_type + " found (length: " + str(chunk_length) + ") at position " + str(self.desc.tell()))
                    self.desc.read(4)
                    return chunk_length
        print(chunk_type + ": not found")
        return False

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
        self.find_chunk("IHDR")
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
        if not self.find_chunk("iTXt"):
            if not self.find_chunk("tEXt"):
                if not self.find_chunk("zTXt"):
                    print("no textual data found")
                else:
                    chunk_size = self.find_chunk("zTXt")
            else:
                chunk_size = self.find_chunk("tEXt")
        else:
            chunk_size = self.find_chunk("iTXt")

        if chunk_size > 0:
            print(self.desc.read(chunk_size).decode('utf-8'))

    def read_content(self):
        chunk_size = self.find_chunk("IDAT")
        self.compressedContent = self.desc.read(chunk_size)

    def add_compressed_content(self, content):
        self.compressedContent = content

    def decompress(self):
        self.content = zlib.decompress(self.compressedContent)
        self.contentSize = len(self.content)

    def create_pixel_array(self):
        for index, pixel in enumerate(self.content):
            if index % (3*self.imageProperties["width"] + 1) is not 0:
                self.pixelArray.append(pixel)

        self.redChannel = []
        self.greenChannel = []
        self.blueChannel = []
        self.pixelArray = list(chunks(self.pixelArray, 3))
        for pixel in self.pixelArray:
            self.redChannel.append(pixel[0])
            self.greenChannel.append(pixel[1])
            self.blueChannel.append(pixel[2])

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
        image_data = b""
        for index, pixel in enumerate(self.content):
            if index % (3 * self.imageProperties["width"] + 1) is not 0:
                image_data += pixel.to_bytes(1, byteorder="big")

        self.keyPair = rsa.RSA(256)
        self.keyPair.generate_key_pairs()
        encoded_data = b""
        encoded_block = b""

        for x in range(1, (self.contentSize // 4) + 1):
            print(encoded_block)
            encoded_block = b""
            for byte in image_data[32*(x-1):32*x]:
                encoded_block += byte.to_bytes(1, byteorder="big")
            encoded_data += self.keyPair.encode(int.from_bytes(encoded_block, byteorder="big")).to_bytes(32, byteorder="big")

        encodedArray = []
        for index, pixel in enumerate(encoded_data):
            encodedArray.append(pixel)

        encodedArray = list(chunks(encodedArray, self.imageProperties["width"]*3))
        self.encodedContent = encoded_data
        print("Encoded:", self.encodedContent)

        png.from_array(encodedArray[:self.imageProperties["width"]][:self.imageProperties["height"]], 'RGB')\
            .save('./img/result.png')

    def decode_with_rsa(self):
        decoded_data = b""
        decoded_block = b""

        for x in range(1, (self.contentSize // 32) + 2):
            decoded_block = b""
            for byte in self.encodedContent[32*x:32*(x+1)]:
                print(byte)
                decoded_block += byte.to_bytes(1, byteorder="big")
            decoded_data += self.keyPair.decode(int.from_bytes(decoded_block, byteorder="big")).to_bytes(32, byteorder="big")
            print("Decoded:", decoded_data)

        print("Decoded:", decoded_data)

        decodedArray = []
        for index, pixel in enumerate(decoded_data):
            decodedArray.append(pixel)

        decodedArray = list(chunks(decodedArray, self.imageProperties["width"]*3))
        print(decodedArray)

        png.from_array(decodedArray[:self.imageProperties["width"]][:self.imageProperties["height"]], 'RGB') \
            .save('./img/result-decoded.png')

##########################################################


originalImage = ImageFile("./img/image50x50.png", "rb")
if originalImage.check_if_png():
    originalImage.update_properties()
    originalImage.read_content()
    originalImage.decompress()
    originalImage.create_pixel_array()
    originalImage.display_properties()
    # originalImage.compute_spectrum("red")
    # originalImage.compute_spectrum("green")
    # originalImage.compute_spectrum("blue")

    originalImage.encode_with_rsa()
    originalImage.decode_with_rsa()

    # flat_pixel_array = []
    # for sublist in originalImage.pixelArray:
    #     for item in sublist:
    #         flat_pixel_array.append(item)
    #
    # final = b""
    # for byte in flat_pixel_array:
    #     final += byte.to_bytes(1, byteorder="big")
    #
    # flat_pixel_array = list(chunks(flat_pixel_array, originalImage.imageProperties["width"]**2))
    # # png.from_array(flat_pixel_array, 'RGB').save('./img/result.png')
    #
    # image_data = int.from_bytes(final, byteorder="big")
    #
    # [n, e, d] = rsa.generate_key_pairs(256)
    #
    # encoded_image = rsa.rsa_encode(n, e, image_data)
    # print(encoded_image.to_bytes(32, byteorder="big"))
    #
    # enc = encoded_image.to_bytes(36, byteorder="big")
    #
    # print("enc", enc)
    #
    # flat_final = []
    # for pixel in enumerate(enc):
    #     print(pixel)
    #     flat_final.append(pixel[1])
    #
    # flat_final = list(chunks(flat_final, originalImage.imageProperties["width"]**2))
    # print(flat_final)
    #
    # png.from_array(flat_final, 'RGB').save('./img/result.png')
    #
    #
    #
    # decoded_image = rsa.rsa_decode(n, d, encoded_image)
    # print(decoded_image.to_bytes(32, byteorder="big"))

else:
    print("Wrong file format")