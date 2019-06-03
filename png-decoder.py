import os
import zlib
import cmath
import numpy as np
import matplotlib.pyplot as plt

fileName = "./img/image0.png"
imageFile = open(fileName, "rb")
fileSize = os.path.getsize(fileName)
print("FILE SIZE (in bytes): " + str(fileSize))

def check_if_png(signature):
    if type(signature) is bytes and signature == b'\x89PNG\r\n\x1a\n':
        return True
    elif type(signature) is str and signature == '89504e470d0a1a0a':
        return True
    elif type(signature) is int and signature == 9894494448401390090:
        return True
    else:
        return False


def find_chunk(chunk_type):
    imageFile.seek(0, 0)
    while imageFile.tell() < fileSize:
        if imageFile.read(1).find(bytes(chunk_type[0], 'utf-8')) != -1:
            if imageFile.read(3).find(bytes(chunk_type[1:4], 'utf-8')) != -1:
                imageFile.seek(-8, 1)
                chunk_length = int.from_bytes(imageFile.read(4), byteorder="big")
                print(chunk_type + " found (length: " + str(chunk_length) + ") at position " + str(imageFile.tell()))
                imageFile.read(4)
                return chunk_length
    print(chunk_type + ": not found")
    return False


# file signature:
fileSig = imageFile.read(8)
intBytes = int.from_bytes(fileSig, byteorder="big")

# file header:
if check_if_png(fileSig):
    
    find_chunk("IHDR")
    
    width = int.from_bytes(imageFile.read(4), byteorder="big")
    height = int.from_bytes(imageFile.read(4), byteorder="big")
    print("IMAGE DIMENSIONS:       " + str(width) + "x" + str(height))
    bitDepth = int.from_bytes(imageFile.read(1), byteorder="big")
    print("BIT DEPTH:              " + str(bitDepth))


    def color_type_switch (color):
        switcher = {
            0: "1 - gray scale",
            2: "3 - true color (RGB)",
            3: "1 - indexed",
            4: "2 - gray scale with alpha",
            6: "4 - RGB with alpha"
        }
        return switcher.get(color, "invalid color type")


    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    colorType = int.from_bytes(imageFile.read(1), byteorder="big")
    print("COLOR TYPE:             " + color_type_switch(colorType))
    compressionMethod = int.from_bytes(imageFile.read(1), byteorder="big")
    if compressionMethod == 0:
        print("COMPRESSION METHOD:     " + str(compressionMethod) + " - deflate")
    else:
        print("COMPRESSION METHOD:     " + str(compressionMethod) + " - unknown method")
    filterMethod = int.from_bytes(imageFile.read(1), byteorder="big")
    if filterMethod == 0:
        print("FILTER METHOD:          " + str(filterMethod) + " - default")
    else:
        print("FILTER METHOD:          " + str(filterMethod) + " - unknown method")
    interlaceMethod = int.from_bytes(imageFile.read(1), byteorder="big")
    if interlaceMethod == 0:
        print("INTERLACE METHOD:       " + str(interlaceMethod) + " - no interlace")
    else:
        print("INTERLACE METHOD:       " + str(interlaceMethod) + " - Adam7")

    if find_chunk("tIME"):
        lastEdit = str(int.from_bytes(imageFile.read(2), byteorder="big"))
        lastEdit += "/"
        lastEdit += str(int.from_bytes(imageFile.read(1), byteorder="big")).zfill(2)
        lastEdit += "/"
        lastEdit += str(int.from_bytes(imageFile.read(1), byteorder="big")).zfill(2)
        lastEdit += " "
        lastEdit += str(int.from_bytes(imageFile.read(1), byteorder="big")).zfill(2)
        lastEdit += ":"
        lastEdit += str(int.from_bytes(imageFile.read(1), byteorder="big")).zfill(2)
        lastEdit += ":"
        lastEdit += str(int.from_bytes(imageFile.read(1), byteorder="big")).zfill(2)
        print(lastEdit)

    chunkSize = 0
    if not find_chunk("iTXt"):
        if not find_chunk("tEXt"):
            if not find_chunk("zTXt"):
                print("no textual data found")
            else:
                chunkSize = find_chunk("zTXt")
        else:
            chunkSize = find_chunk("tEXt")
    else:
        chunkSize = find_chunk("iTXt")

    if chunkSize > 0:
        print(imageFile.read(chunkSize).decode('utf-8'))

    find_chunk("hIST")
    find_chunk("gAMA")
    find_chunk("cHRM")

    chunkSize = find_chunk("IDAT")
    data = imageFile.read(chunkSize)
    pixelArray = []
    print(data)
    decompressed = zlib.decompress(data)
    print(decompressed)
    for index, pixel in enumerate(decompressed):
        if index % (3*width + 1) is not 0:
            pixelArray.append(pixel)

    redChannel = []
    greenChannel = []
    blueChannel = []
    pixelArray = list(chunks(pixelArray, 3))
    print(pixelArray)
    for pixel in pixelArray:
        redChannel.append(pixel[0])
        greenChannel.append(pixel[1])
        blueChannel.append(pixel[2])

    red_spectrum = np.fft.fft(redChannel[:1024])
    red_spectrum_amp = np.abs(red_spectrum)
    plt.plot(red_spectrum_amp)
    plt.show()

    green_spectrum = np.fft.fft(greenChannel[:1024])
    green_spectrum_amp = np.abs(green_spectrum)
    plt.plot(green_spectrum_amp)
    plt.show()

    blue_spectrum = np.fft.fft(blueChannel[:1024])
    blue_spectrum_amp = np.abs(blue_spectrum)
    plt.plot(blue_spectrum_amp)
    plt.show()

else:
    print("wrong file format")
