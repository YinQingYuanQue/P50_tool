#-------------------------------------------------------------------------------
# Name:        Landform Classification Module
# Purpose:     Calculates deviation from mean elevation (DEV) raster from
#              digital elevation model (DEM)
#
# Author:      dbeene
#
# Created:     12/22/2020
# Copyright:   (c) dbeene 2020
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

# Import modules
import arcpy, os
from arcpy import env
from arcpy.sa import *
# Check out Spatial extension, handle errors
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

    # Set environments
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = r'D:\M_3\P50\july\0720\01-CRST' # Workspace
    DEM = arcpy.GetParameterAsText(0) # Define DEM
    arcpy.env.mask = DEM # Set DEM as raster analysis mask
    arcpy.env.extent = DEM
    arcpy.env.cellSize = DEM
    # User input, neighborhood shape and size:
    shape = arcpy.GetParameterAsText(1) # Set tkinter dropdown to include ("NbrAnnulus", "NbrCircle", "NbrRectangle")
    # Conditional input based on neighborhood shape. Limited to three shapes for now
    if shape == "NbrAnnulus":
        inr = raw_input("Inner radius: ") # Numeric only
        outr = raw_input("Outer radius: ") # Numeric only
        unit = raw_input("Units (CELL or MAP): ") # Dropdown include ("CELL", "MAP")
        units = str('('), inr, str(', '), outr, str(', "') + unit + str('")')
    if shape == "NbrCircle":
        rad = raw_input("Radius: ") # Numeric only
        unit = raw_input("Units (CELL or MAP): ") # Dropdown include ("CELL", "MAP")
        units = str('('), rad, str(', "') + unit + str('")')
    if shape == "NbrRectangle":
        width = raw_input("Width: ") # Numeric only
        height = raw_input("Height: ") # Numeric only
        unit = raw_input("Units (CELL or MAP): ") # Dropdown include ("CELL", "MAP")
        units = str('('), width, str(', '), height, str(', "') + unit + str('")')
    def neighborhood(a,b):
        print a + str().join(b)
##    neighborhood = shape + str().join(units)
    # Set focal mean/std variables
    focalmean = FocalStatistics(DEM, neighborhood(shape, units), "MEAN", "DATA") # Error here, neighborhood prints with ''
    focalstd = FocalStatistics(DEM, neighborhood(shape, units), "STD", "DATA")
    # Calculate topographic position as DEM - focal mean
    TPI = Minus(DEM, focalmean)
    # Calculate deviation from mean elevation (DEV) raster as
    # (TPI - focal mean)/focal stdev
    DEV_tmp = Divide(Minus(TPI, focalmean),focalstd)
    # If stdev = 0, it returns NoData cells - replace with 0
    # Raster calculator expression:
        # Con(IsNull("DEV_tmp"),0,"DEV_tmp")
    DEV_tmp = Con(IsNull(DEV_tmp),0,DEV_tmp)
    # Standardize DEV raster:
    # Constant mean
    devmean = CreateConstantRaster(arcpy.management.GetRasterProperties(DEV_tmp, "MEAN"), "FLOAT")
    # Constant standard deviation
    devstd = CreateConstantRaster(arcpy.management.GetRasterProperties(DEV_tmp, "STD"), "FLOAT")
    # Calculate raster
    DEV = Divide(Minus(DEV_tmp, devmean), devstd)
    DEV.save(arcpy.env.workspace + '\dev')
    # Classify DEV into landforms
    # Get min/max of DEV raster
    DEVminResult = arcpy.GetRasterProperties_management(DEV, "MINIMUM")
    DEVmaxResult = arcpy.GetRasterProperties_management(DEV, "MAXIMUM")

    DEVmin = float(DEVminResult.getOutput(0))
    DEVmax = float(DEVmaxResult.getOutput(0))

    # Gather user input to define landform classification schema
        # Provide description above these cells:
        # Landforms are classified from the deviaiton of mean elevation (DEV)
        # raster. Default values are provided in the cells below, but they are
        # dependent on spatial context and user input.

        # The list below reclassifies a raster using the format [from,to,output]
        # `from` and `to` will be populated from cells in the GUI, with the exception of DEVmin and DEVmax
        # The values in the list now should be default in the GUI cells
        # Landform types = valleys, lower slopes, flat slopes, middle slopes, upper slopes, ridges
##    reclasslist = [[DEVmin,-1,1],[-1,-0.5,2],[-0.5,0,3],[0,0.5,4],[0.5,1,5],[1,DEVmax,6]]
    reclasslist = [[DEVmin,-1,1],[-1,-0.5,2],[-0.5,0,3],[0,0.5,4],[0.5,DEVmax,5]] # Remove line after user input is defined
    if DEVmax < 0.5: # Change to if DEVmax < any number user specifies in GUI cells
        print('Maximum DEV raster value ('+ DEVmax + ') is less than maximum specified remap value. The remap table is invalid.')
    else:
    # Reclassify
        landforms = Reclassify(DEV, "Value", RemapRange(reclasslist), "NODATA")
        # Save raster
        landforms.save(arcpy.env.workspace + '\landforms')
    # Symbolize landform raster
    # Clear workspace
    del focalmean
    del focalstd
    del DEV_tmp
##    del DEV
    del devmean
    del devstd
    del TPI

# Check in SA extension
    arcpy.CheckInExtension("Spatial")

else:
    print "Spatial Analyst license is not available."