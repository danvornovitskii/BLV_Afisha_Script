# This script combines two images into one of dimensions 600x360. 
# IMG1 should be 600x300. 

import cv2
import numpy as np
import datetime
import os
import subprocess
import requests 
import pprint
import pyperclip

def combine_images(image_path1, image_path2, base_output_path, output_filename):
    # Load the images
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    # Resize img1 to 600x300 if it's not already that size
    if img1.shape[1] != 600 or img1.shape[0] != 300:
        img1 = cv2.resize(img1, (600, 300))

    # Check if images loaded successfully
    if img1 is None or img2 is None:
        print("Error: One of the images did not load. Check the file paths.")
        return

    # Combine the images vertically
    combined_img = np.vstack((img1, img2))

    # Get today's date in YYYY-MM-DD format
    today = datetime.date.today().isoformat()

    # Create a new folder named after today's date
    date_folder_path = os.path.join(base_output_path, today)
    if not os.path.exists(date_folder_path):
        os.makedirs(date_folder_path)

    # Define the output file path within the new date-named folder
    output_file_path = os.path.join(date_folder_path, output_filename)

    # Save the combined image
    cv2.imwrite(output_file_path, combined_img)
    print(f"Combined image saved as {output_file_path}")

    # Delete img1 after combining
    try:
        os.remove(image_path1)
        print(f"Image 1 deleted: {image_path1}")
    except Exception as e:
        print(f"Error deleting Image 1: {e}")

    # Return the full path of the saved image
    return output_file_path

def create_video(image_path, video_length, fps=25):
    # Load the combined image
    img = cv2.imread(image_path)
    height, width, layers = img.shape

    # Define the video output path (same as image path but with .mp4 extension)
    video_output_path = image_path.replace('.jpg', '.mp4')

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for .mp4 files
    video = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

    # Calculate the total number of frames
    total_frames = video_length * fps

    # Write each frame to the video file
    for _ in range(total_frames):
        video.write(img)

    # Release the video writer
    video.release()
    print(f"Video saved as {video_output_path}")

    # Delete the combined image after creating the video
    try:
        os.remove(image_path)
        print(f"Combined image deleted: {image_path}")
    except Exception as e:
        print(f"Error deleting the combined image: {e}")

    return video_output_path

def reduce_bitrate(video_path, target_bitrate="1500k"):
    # Temporary output video path
    temp_output_video_path = video_path.replace(".mp4", "_temp.mp4")
    
    # FFmpeg command to reduce the bitrate
    command = [
        'ffmpeg', '-i', video_path, '-b:v', target_bitrate,
        '-bufsize', target_bitrate, '-maxrate', target_bitrate,
        temp_output_video_path
    ]
    
    try:
        # Execute FFmpeg command
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # Overwrite the original file with the reduced bitrate version
        os.rename(temp_output_video_path, video_path)
        print("Original file replaced successfully with reduced bitrate version.")
        return video_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to reduce bitrate: {e}")
    except Exception as e:
        print(f"Error during file replacement: {e}")

################### Yandex Disk Integrations
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
public_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
TOKEN = 'y0_AgAAAAA3Qp8VAADLWwAAAAD8hU8WAADxbbacRWBGKaIKYIHn8795va9d2g'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}

def create_folder(path):
    # Создание папки. \n path: Путь к создаваемой папке
    requests.put(f'{URL}?path=/Mercury%20WORK/Barvikha%20Screen/{path}', headers=headers)

    return f'/Mercury%20WORK/Barvikha%20Screen/{path}'


def upload_file(loadfile, savefile, replace=False):
    #Загрузка файла.
    #savefile: Путь к файлу на Диске
    #loadfile: Путь к загружаемому файлу
    #replace: true or false Замена файла на Диск
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)

def publish_file(path):
    res = requests.put(f'{URL}/publish?path={path}', headers=headers)
    meta = requests.get(f'{URL}/?path={path}', headers=headers).json()
    pyperclip.copy(meta['public_url'])
    print('Public URL copied to the clipboard.')

########################################

# Fixed path for img2
image_path2 = '/Users/danvornovitskii/Documents/Mercury Storage/Barvikha/blv_screen_bottom.jpg'  # Update this to your img2's actual path

# Base output directory
base_output_path = '/Users/danvornovitskii/Documents/Mercury Work/Barvikha'

# Prompt user to enter the path for img1
image_path1 = input("Enter the path for the first image (img1): ").strip()

# Prompt user to enter the desired output filename without the extension
output_filename_input = input("Enter the desired output filename without extension (e.g., 'combined_image'): ").strip()

# Append '.jpg' extension to the output filename, avoiding double extension if already provided
output_filename = f"{output_filename_input}.jpg" if not output_filename_input.lower().endswith('.jpg') else output_filename_input

output_file_path = combine_images(image_path1, image_path2, base_output_path, output_filename)

# Prompt user to enter the desired length of the video in seconds
video_length = int(input("Enter the desired video length in seconds: "))

# Call the create_video function with the path of the combined image, the input video length, and fps
video_output_path = create_video(output_file_path, video_length)

# Reduce video bitrate to 1500
final_video_path = reduce_bitrate(video_output_path)

# Create folder in Yandex Disk with today's date
today = datetime.date.today().isoformat()
yandex_folder_path = create_folder(today)

upload_file(final_video_path, f'{yandex_folder_path}/{output_filename_input}.mp4')
publish_file(yandex_folder_path)
# print(f'https://disk.yandex.ru/client/disk/{yandex_folder_path}')