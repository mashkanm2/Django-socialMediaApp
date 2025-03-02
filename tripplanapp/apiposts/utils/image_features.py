

from PIL import ExifTags, Image


def _decimal_coords(coords, ref):
    ## refrence => https://stackoverflow.com/questions/64113710/extracting-gps-coordinates-from-image-using-python
    decimal_degrees = float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
    if ref == "S" or ref =='W' :
        decimal_degrees = -1 * decimal_degrees
    return decimal_degrees



def image_coordinates(image:Image):
    '''
    ret_={
        'GPSLatitude': 52.314166666666665,
        'GPSLongitude': 4.941}
    '''
    GPSINFO_TAG = next(tag for tag, name in ExifTags.TAGS.items() if name == "GPSInfo")
    
    info = image.getexif()

    gpsinfo = info.get_ifd(GPSINFO_TAG)
    if len(gpsinfo):
        try:
            res_={'GPSLatitude' : _decimal_coords(gpsinfo[2], gpsinfo[1]),
                  'GPSLongitude' : _decimal_coords(gpsinfo[4], gpsinfo[3])
                  }
            return {"sucess":True,"result":res_}
        except AttributeError:
            return {"sucess":False,"result":"No Coordinates"}
    else:
        return {"sucess":False,"result":"The Image has no EXIF information"}

    




    
    
    

    
