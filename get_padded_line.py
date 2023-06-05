#!/home/geo2/anaconda3/bin/python

import os
import re
import sys
import glob
import pandas as pd

def get_analyze_file(serial):
    '''returns path to analyze file from the serial number'''
    os.chdir("/")
    path_list = glob.glob(f"./dl*/RawImageRepairs/*/sn{serial}_analyze.csv")
    if len(path_list) == 0:
        print(f"No sn{serial}_analyze.csv found")
    elif len(path_list) > 1:
        print(f"Found: {len(path_list)} files with serial {serial}, returning {os.path.basename(path_list[0])}.")
        return path_list[0]
    else:
        return path_list[0]

def read_analyze_file(path_to_file):
    '''read the sn***analyze.csv and return it in form of DataFrame'''
    af_df = pd.read_csv(path_to_file)
    return(af_df)

def get_sn(file_name):
    '''return bumper from file name in format sn****analyze.csv'''
    nb_list = re.findall(r'\d+',file_name)
    return(nb_list[0])


def append_padded(file_in, line):
    '''append the line to padded file'''
    #chceck if line already exits
    with open(file_in, 'r', encoding= 'utf-8') as file:
        lines = file.readlines()
    if line in lines:
        line = re.sub('\s+',' ', line)
        print(f"File {os.path.basename(file_in)} already contains line {line.strip()}")
    else:
        try:
            with open(file_in,'a', encoding = 'utf-8') as file:
                file.write(line)
                print(f"{line.strip()} added to {os.path.basename(file_in)}")
        except (IOError, OSError) as exc:
            print(f"Something went wrong: {exc}")

def read_4d_nav(nav_file):
    '''Read 4dnav file and return pandas DataFrame containing particular columns'''
    if os.path.exists(nav_file) and os.stat(nav_file).st_size != 0:
        try:
            nav_df = pd. read_csv(nav_file, skiprows = 8)
            nav_df = nav_df[["Line","Point","NodeCode","Index"]]
            return nav_df
        except (IOError, OSError) as exc:
            print(f"Error reading {os.path.basename(nav_file)}: {exc}")
            return None
    else:
        print(f"File {os.path.basename(nav_file)} doesn't exist or is an empty file")
        return None

def get_bmp_sn(file_in, serial):
    '''get bumper number from serial number'''
    try:
        bmp_df = pd.read_csv(file_in, sep = "\s+", names = ["Bumper", "Serial"] )
        serial_df = bmp_df.query(f"Serial == {serial}")
        return(serial_df['Bumper'].values[0])
    except (IOError, OSError) as exc:
        print(f"Error reading {os.path.basename(file_in)}: {exc}")
        return None

def main():
    '''main function'''  
    analyze_file = get_analyze_file(serial_number)
    if analyze_file:
        print(f"Found file: {analyze_file}")
    else:
        sys.exit(1)   
    
    analyze_file_df = read_analyze_file(analyze_file)
    gp_df = analyze_file_df.query('delta != 1')         #find the line where time delta exceeds 1 second
    
    if len(gp_df) == 0:                                 #if no such line
        print(f"No padded samples in {os.path.basename(analyze_file)}. Exiting ...")
        sys.exit(1)
    else:
        dct = gp_df.to_dict(orient='records')[0]        #convert to dictionary for some reason
        stop = int(dct['second'])                       #get the last second af gap
        start = stop - int(dct['delta']) +1             #get the first second of gap
  
        bumper = get_bmp_sn(bmp_sn_file, serial_number) #get bumper using serial
        #print(bumper)

        nav_df = read_4d_nav(fdnav_file)
        line_pnt = nav_df.query(f"NodeCode == {bumper}")
        line_dct = line_pnt.to_dict(orient='records')[0]
        line = line_dct['Line']
        point = line_dct['Point']
        index = line_dct['Index']

        padded_line = f"{line}\t\t{point}\t\t\t{index}\t\t\t{start}\t\t{stop}\n" 
        #print(padded_line)
        append_padded(padded_file,padded_line)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage {sys.argv[0]} serial number")
    else:
        serial_number = sys.argv[1]
        #padded_file = r"/home/geo2/Public/scr/zdmefr/02_SSD_help_tools/padded_nodes.txt"
        padded_file = r"/qc/06-ARAM/padding/padded_nodes.txt"
        fdnav_file = r"/qc/06-ARAM/nav/Postplot_R/4dnav_lines/BR001522_4dnav.csv"
        bmp_sn_file = r"/qc/06-ARAM/parameters/AllMantaNodes_bumper_rsn.txt"
        main()
