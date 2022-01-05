import arcpy
import math
#import major_interface
import time
import os
from arcpy.sa import *
from arcpy import env

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

arcpy.AddMessage('Start at 2021')

receptor = arcpy.GetParameterAsText(0)
rec_x = arcpy.GetParameterAsText(1)
rec_y = arcpy.GetParameterAsText(2)
pollution = arcpy.GetParameterAsText(3)
pol_x = arcpy.GetParameterAsText(4)
pol_y = arcpy.GetParameterAsText(5)
Pollution_area = arcpy.GetParameterAsText(6)
Dist_tre = arcpy.GetParameterAsText(7)

output = arcpy.GetParameterAsText(8)

arcpy.AddMessage('Start')

if len(Dist_tre)>0:    
    Dist_tre = float(Dist_tre) * 1000    
else:
    Dist_tre = 50000000
#t_local = time.localtime()
#output = output + '/' + str(t_local[0]) + str(t_local[1]) + str(t_local[2])+ str(t_local[3])
#os.mkdir(output)
arcpy.workspace = output

def get_distance(a,b):
	return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

		
arcpy.AddMessage('read in receptor and pollution data')
cursors_pollutions = arcpy.da.SearchCursor(pollution,[pol_x,pol_y])

		#change on 2021/4/24 for data without size information
total_length = 0
for each in cursors_pollutions:
    total_length += 1
print('****: total_length  ', total_length)		
#pollution_size = []
		
#for i in range(total_length):			
#    pollution_size.append(1)		
#arcpy.AddField_management(pollution,'SqrtArea','Double')	

cursors_FID = arcpy.da.SearchCursor(receptor,['FID'])		
cursors_receptors = arcpy.da.SearchCursor(receptor,[rec_x,rec_y])
		
locations_pollution=[]		
locations_receptor=[]		
areas_pollution=[]		
FID = []		
IN_FID=[]

		
cursors_pollutions = arcpy.da.SearchCursor(pollution,[pol_x,pol_y])		
for each in cursors_pollutions:			
    locations_pollution.append(each)

for each in cursors_receptors:			
    locations_receptor.append(each)

for each in cursors_FID:			
    FID.append(each)
					
arcpy.AddMessage('Calculating wind proximity')		
index = []
		
#print('length: ', len(weights))		
#print('length: ', len(locations_receptor))		
#print('length: ', len(locations_pollution))
		
for i in range(len(locations_receptor)):			
    result=0		
    	
    for j in range(len(locations_pollution)):
        dis_r_p = get_distance(locations_receptor[i],locations_pollution[j])
        if dis_r_p <= Dist_tre:
            temp = (1/dis_r_p)
        else:
            temp = 0
        #temp1 = (weights[j]/get_distance(locations_receptor[i],locations_pollution[j]))            		
        if(math.isnan(temp)):
            continue
        
        result = result+temp
        #result1 = result1+temp1
    result=math.sqrt(result)
    #result1 = math.sqrt(result1)
    index.append(result)
    #index1.append(result1)
		
arcpy.AddMessage('writing the result to: '+receptor)
		#add field of wind priximity
arcpy.AddField_management(receptor,'New_Prox','Double')
#arcpy.AddField_management(receptor,'Prox_size','Double')
with arcpy.da.UpdateCursor(receptor, ['New_Prox']) as cursor:			
    count=0			
    for row in cursor:				
        row[0]=index[count]		
        #row[1]=index1[count]		
        count+=1				
        cursor.updateRow(row)	

IDW_out = Idw(receptor, "New_Prox")
out_fuzzy = FuzzyMembership(IDW_out,FuzzyLarge())

out_fuzzy.save(output+'\\Proximity_fz')

arcpy.AddMessage('wind proximity processing DONE')


if len(Pollution_area)>0:
    Sum_size= 0
    with arcpy.da.SearchCursor(pollution, Pollution_area) as cursor:			
    #count=0			
        for row in cursor:
            Sum_size = Sum_size + row[0]				
        #row[0]=pollution_size[count]				
        #count+=1				
        #cursor.updateRow(row)	
		#End of change on 2021/4/24
    arcpy.AddWarning(Sum_size)
    
    arcpy.AddField_management(pollution,'SqtA_new','Double')
    with arcpy.da.UpdateCursor(pollution, [Pollution_area,'SqtA_new']) as cursor:
        for row1 in cursor:
            row1[1] = math.sqrt(row1[0]/Sum_size)
            cursor.updateRow(row1)
            
    cursors_areas = arcpy.da.SearchCursor(pollution,['SqtA_new'])		
    
    for each in cursors_areas:			
        areas_pollution.append(each)

    weights=[]		
    for each in areas_pollution:			
        weights.append(each[0])
       
    index1 = []
    for i in range(len(locations_receptor)):			
        result1 = 0	
        for j in range(len(weights)):
            dis_r_p = get_distance(locations_receptor[i],locations_pollution[j])
            if dis_r_p <= Dist_tre:
        #temp = (1/get_distance(locations_receptor[i],locations_pollution[j]))
                temp1 = (weights[j]/dis_r_p)    
            else:
                temp1 = 0        		
        
            if(math.isnan(temp1)):
                continue
        #result = result+temp
            result1 = result1+temp1
    #result=math.sqrt(result)
        result1 = math.sqrt(result1)
    #index.append(result)
        index1.append(result1)
    
    arcpy.AddField_management(receptor,'Prox_size','Double')
    with arcpy.da.UpdateCursor(receptor, ['Prox_size']) as cursor:			
        count=0			
        for row in cursor:				
            row[0]=index1[count]		
        #row[1]=index1[count]		
            count+=1				
            cursor.updateRow(row)	
        
    IDW_out1 = Idw(receptor, "Prox_size")
    out_fuzzy1 = FuzzyMembership(IDW_out1,FuzzyLarge())
    out_fuzzy1.save(output+'\\Prox_size_fz')