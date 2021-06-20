import re
import os
import time
import argparse
from os import walk
from videoprops import get_video_properties
import subprocess

parser = argparse.ArgumentParser(description='Convert to HEVC video encoder.')
parser.add_argument(
        '-r', '--root_path', required=True, type=str, help='input root video directory path')
parser.add_argument(
        '-dof', '--deleteOriginalFile', required=False, type=bool, default=False , help='delete Original File')
parser.add_argument(
        '-cf', '--complexFFmpeg', required=False, type=bool, default=False , help='complex ffmpeg')       
parser.add_argument(
        '-ov', '--overWriteVid', required=False, type=bool, default=False , help='overwrite the ffmpeg output file')   
args = parser.parse_args()

root_path = args.root_path
complexFFmpeg = args.complexFFmpeg
overWriteVid = args.overWriteVid
deleteOriginalFile = args.deleteOriginalFile

def convert2Hevc(dir_path, deleteOriginalFile = False, complexFFmpeg = False, overWriteVid = False):
    dirpath, dirnames, filenames = next(walk(dir_path))
    print("working in directory " + dirpath)
    print("config: deleteOriginalFile={delete}, complexFFmpeg={complex}, overWriteVid={over}".format(delete=deleteOriginalFile, complex=complexFFmpeg, over=overWriteVid))    
    for directory in dirnames:
        if("HEVC" in directory):
            print("skipping dierctory " + directory + " haves HEVC in the file name")
            continue
        convert2Hevc(dirpath + "/" + directory,
            deleteOriginalFile=deleteOriginalFile, 
            complexFFmpeg=complexFFmpeg, 
            overWriteVid=overWriteVid)
        time.sleep(5)

    for vid in filenames:
        filename, file_extension = os.path.splitext(vid)
        if(file_extension != ".mkv" and file_extension != ".mp4"): 
            continue
        newVidName = re.sub(r'^\[.*?\]', '', filename).strip() + file_extension
        os.rename(dirpath + "/" + vid, dirpath + "/" + newVidName)
        if(("HEVC" in filename) or ("hevc" in filename)):
            print("skipping video " + filename + " haves HEVC in the file name")
            continue
        props = get_video_properties(dir_path + "/" + newVidName)
        if (props['codec_name'] == "hevc"): 
            print("skipping video " + filename + " alredy incoded with HEVC")
            continue
        returnCode = runFFMpeg(dir_path, newVidName, complexFFmpeg, overWriteVid)
        # time.sleep(3)
        if(returnCode == 0):
            if(deleteOriginalFile):
                print("deleting original file [{file}]".format(file= dirpath + "/" + newVidName))
                os.remove(dirpath + "/" + newVidName)
        else:
            if(returnCode != -1):
                print("fmmpeg command error for file {}".format(dirpath + "/" + newVidName))


def runFFMpeg(filePath, videoName, complexFFmpeg = False, overWriteVid = False): 
    filename, _ = os.path.splitext(videoName)
    newVidName = re.sub(r'^\[.*?\]', '', filename).strip()
    if(not overWriteVid and os.path.exists(filePath + "/" + newVidName + "[HEVC].mkv")): 
        print("skipping file {} becouse it's alredy there".format(filePath + "/" + newVidName))
        return -1
    if(complexFFmpeg):
        ffmpegArgs =  "-y -loglevel warning -hide_banner -stats -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -hwaccel_device 0 -c:v:0 h264_cuvid"
        hevc_nvencArgs = "-vf \"hwdownload,format=nv12\" -c copy -c:v:0 hevc_nvenc -profile:v main10 -pix_fmt p010le -rc:v:0 vbr -tune hq -preset p5 -multipass 1 -bf 4 -b_ref_mode 1 -nonref_p 1 -rc-lookahead 75 -spatial-aq 1 -aq-strength 8 -temporal-aq 1 -cq 21 -qmin 1 -qmax 99 -b:v:0 2M -maxrate:v:0 5M -map 0"
    else:
        ffmpegArgs =  "-y -loglevel warning -hide_banner -stats -vsync 0"
        hevc_nvencArgs = "-c:v hevc_nvenc -profile:v main10 -pix_fmt p010le -preset p5 -map 0"
    command = 'ffmpeg {ffmpegArgs} -i "{vidPath}" {hevc_nvencArgs} "{newVidPath}[HEVC].mkv"'.format(ffmpegArgs=ffmpegArgs,
                                                    vidPath=filePath + "/" + videoName, 
                                                    hevc_nvencArgs=hevc_nvencArgs,
                                                    newVidPath=filePath + "/" + newVidName)   
    process = subprocess.Popen(command, 
                        stdout=subprocess.PIPE,
                        universal_newlines=True)
    while True:
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            return return_code



    

convert2Hevc(root_path, 
    deleteOriginalFile=deleteOriginalFile, 
    complexFFmpeg=complexFFmpeg, 
    overWriteVid=overWriteVid)


