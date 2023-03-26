# qrCodeImageSorterGUI
GUI interface for the [qrCodeImageSorter](https://github.com/jonpecar/qrCodeImageSorter) repository. For detailed information on the philosophy 
of the tool see the readme in this repository. This is a GUI interface for this underlying toolset.

## A Quick (but rough) Video Guide

https://user-images.githubusercontent.com/65805625/192924326-2560853a-2418-4b95-8806-40d787ae489c.mp4

## Installation

To install the tool, run the below command with any version of Python above 3.7:

```pip install qrImageIndexerGUI```

## Instructions
---

### Launch Window
---

To load the launch window, run the command:

```python -m qrImageIndexerGUI```

This will present the user with the following window:

![LaunchWindow](https://user-images.githubusercontent.com/65805625/192664386-c3fbaa5d-0c27-4b17-a002-9fda23ee2b8c.png)

From here you can open either the window for generating the QR codes or for sorting the resultant images.

### Generate QR Codes
---

This window allows the user to generate QR codes. It also provides a preview of what the output PDF will look like:
![GenerateWindow](https://user-images.githubusercontent.com/65805625/192664832-50818c4c-df25-40ef-aa98-2464f4f8fc4b.png)

The available controls are listed below:
1. Save PDF generated based on the listed inputs to file;
2. Update sample PDF based on the listed inputs;
3. Toggle sorting of PDF for slicing or down the page;
4. Toggle generating QR codes for heading lines;
5. Toggle reapeating of parent headings on every line of the PDF;
6. Toggle inclusion of a prefix in the QR code;
7. Configure prefix to include;
8. Tab-delineated item input;
9. Sample PDF display.

The recommended settings are set by default. In most situations the user should just enter their own text in the 
text entry field (8).

### Sort Images
---

This window allows the user to sort photos that have been taken with QR codes in them. The interface will look similar to the below. 
Note that the provided screenshot is shown after having scanned a folder of images for demonstration. It will be blank prior to this:
![SortPhotos](https://user-images.githubusercontent.com/65805625/192665979-34d9561e-2936-4c20-b17e-71a4f4f961f5.png)

The available controls are listed below:
1. Scan images from a selected directory. This will open a prompt asking the user to select a directory;
2. Save sorted images in a directory. This will save the images in the folder structure dictaged by the detected QR codes;
3. Progress bar to indicate image scanning progress;
4. Indicate whether QR codes have a prefix attached;
5. Specify QR code prefix if used;
6. Display images where QR codes are detected;

    6.1. Path to specified image;
    
    6.2. Thumbnail of image;
    
    6.3. Path detected in QR code.

#### Not Shown: New Feature - Quick Sort

There is now a quick sort button. This button will combine the scanning and saving process. You will be
prompted for 2 directories, first the input and then the output. Images will be scanned then when
scanning is complete they will be saved directly to the output directory without displaying the images
in the window.

This will improve performance where large numbers of images loading into the viewing window was
reducing the processing speed.


#### Note on future feature
---

It is intended that a feature will be added to allow users to manually add images as key images where they are not detected with a QR code. 
This will allow users to images where the QR code may not have been detected or where it was forgotten. That is the primary purpose of the
intermediate preview window but this feature is not implemented yet.
