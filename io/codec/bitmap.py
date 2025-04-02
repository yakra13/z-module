from dataclasses import dataclass
from codec import Codec
from model import Model
from types.int import Int16, Int32, UInt16, UInt32


@dataclass
class BitmapModel(Model): #there are different versions... using windows BITMAPINFOHEADER
    header: UInt16
    bitmap_size_in_bytes: UInt32
    reserved_0: UInt16
    reserved_1: UInt16
    image_data_offset: UInt32
    dib_size: UInt32
    bitmap_width: Int32
    bitmap_height: Int32
    color_planes: UInt16 = 1
    bits_per_pixel: UInt16
    compression: UInt32
    image_size_in_bytes: UInt32
    horizontal_resolution: Int32
    vertical_resolution: Int32
    palette_color_count: UInt32
    important_color_count: UInt32

#Value  id                  compression method              comments
#------------------------------------------------------------------------------------------------------------
# 0 	BI_RGB 	            none             	            Most common
# 1 	BI_RLE8 	        RLE 8-bit/pixel 	            Can be used only with 8-bit/pixel bitmaps
# 2 	BI_RLE4 	        RLE 4-bit/pixel 	            Can be used only with 4-bit/pixel bitmaps
# 3 	BI_BITFIELDS 	    OS22XBITMAPHEADER: Huffman 1D 	BITMAPV2INFOHEADER: RGB bit field masks,BITMAPV3INFOHEADER+: RGBA
# 4 	BI_JPEG 	        OS22XBITMAPHEADER: RLE-24 	    BITMAPV4INFOHEADER+: JPEG image for printing
# 5 	BI_PNG 		                                        BITMAPV4INFOHEADER+: PNG image for printing
# 6 	BI_ALPHABITFIELDS   RGBA bit field masks 	        only Windows CE 5.0 with .NET 4.0 or later
# 11 	BI_CMYK 	        none 	                        only Windows Metafile CMYK
# 12 	BI_CMYKRLE8 	    RLE-8 	                        only Windows Metafile CMYK
# 13 	BI_CMYKRLE4 	    RLE-4 	                        only Windows Metafile CMYK 

class BitmapCodec(Codec):
    def decode(self, content: bytes) -> BitmapModel:
        return super().decode(content)

    def encode(self, data_model: BitmapModel) -> bytes:
        return super().encode(data_model)
