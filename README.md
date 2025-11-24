# Introduction :
**QuickServe** is a project we developed as part of our "Design Thinking" project. Our goal was to identify a design issue and come up with a solution. QuickServe is an IoT enabled solution that aims to reduce the wait time to receive food after a student or faculty places an order.


Users can check the cafeteria's website to see if the cafeteria is crowded or not and based on that info, they can decide whether or not to dine at the cafeteria. Users can also check a physical sign board in front of the canteen for the same info.


## Problem statement :
Users (students/faculty) who utilize the canteen facilities of the college often have to wait a long time for their meal after paying for their meals, leading to them being late to classes.  Users wish that they had a solution that enables them to decide where to go to have lunch during rush hours to have food without having to wait for a long time.


## Implementation details :
* A QR code system is used to keep track of the current number of available "plates".
* A plate is said to be "in use" if a person is currently dining. A plate is "available" when users are done having their food and the plate has been cleaned.
* By keeping track of this info, we can see when there might be possible delays due to not having enough available plates during rush hours.
* Users can look at the live data and decide whether or not to wait during peak hours. This helps users save time by not having to wait a long time after placing an order.
* The process of keeping count of the plates and updating the signage is done by our system.
* The only process where the staff has to be involved is when they have to scan-in or scan-out plates as users place orders or when they return the plates.
* This ensures a seamless experience for the user.

This flowchart shows how the users might interact with the system.
![flowchart](https://github.com/karthik4j/Quick-Serve/blob/main/images/user-interaction.png?raw=true)
**User :** The user is anyone who wishes to have lunch from the college canteen.
**Staff :** Cashiers, people at the food counter, the people involved in cleaning the plates
* Initially when a user orders some food, the user goes to the food counter to get the food.
* The staff at the counter has to scan the plate into the system before serving food.
* This updates the database and the notice board.
*  This action “decrements” the number of plates available for use.
*  After the user is done having their food, they can return the plates to be cleaned.
* The cleaning staff cleans the plates and then scans it into the database one by one.
* This updates the database and “increments” the number of available plates.
* When a user wants to have food at the canteen they can check the board.
* If they don't want to wait for a long time then they can find other places around the campus where they can eat.
* If they are ready to wait, they can proceed to the cafeteria.


The goal of this system is to provide the user's with the necessary info so that they can decide if they want to wait or make new plans based on the count. This helps them to save time and reduce congestion near the food counter.
# Tools used : Both software and hardware tools
## Python
* Tkinter  to create the user interface
* TTKbootstrap to stylize the UI
* OpenCV  to capture the video feed and decode the QR code
* SQLlite3 to store plate info
* http server & socketserver for locally hosting and communicating with the website and digital sign




## Hardware :
* LOLIN D1 mini to fetch information from the web-server.
* JHD659 B/W  (16x2 LCD display) to display information to the user.
# How it works :
* This software interface is meant to be only used by the staff.
* The software is designed to accommodate the staff needs.


### Features supported by the software :
* The software allows the staff member to generate QR codes for each plate. "Generate" here means assigning an unique ID for each plate which is used to keep track of the state. Once a QR code has been generated. It is stored in a folder called "qr_codes", allowing the staff member to print QR codes for plates.
* The software also allows the staff member to combine multiple generated QR codes into a single file for ease of convenience to print.
* When a QR code is removed from the system, the corresponding image is also removed from the folder.
* The Software acts as a web server to host the website that can be used by end users to see the current availability of plates.
* The webserver is also responsible for communicating with the digital sign wirelessly.




Here are some screenshots of the app :
## Menu page :
 * The staff can scan-in or scan-out
 * This page acts as the menu page, allowing users to navigate to other pages.
 * Refresh button is used to refresh the counter on the page.
![1.](https://github.com/karthik4j/Quick-Serve/blob/main/images/1.png?raw=true)




## Database page
 * The database page is used by the staff to see which all plates are in use.
 * The refresh button is used to refresh this data.
 * The Drop database button is used to remove all records from the table.
 * When a staff member chooses to drop the database, the QR codes generated for the plates are removed.
 * When plates are marked as 1, it means they are available for use
 * When plates are marked as 0, it means they are in use.
 ![2.](https://github.com/karthik4j/Quick-Serve/blob/main/images/2.png?raw=true)
## QR code management page :
* This page is used by the staff to generate new QR codes for new plates.
* After a new plate has been added into the system, an image corresponding
* **Combine QR codes:** allows the user to combine multiple QR codes to be combined into a single file so it is easier to print.
* Remove QR is a button used to remove a specific plate from the database. When the correct plate_id is entered, it removes the plate from the database and deletes the QR code stored in the QR_code folder.
![3.](https://github.com/karthik4j/Quick-Serve/blob/main/images/3.png?raw=true)
## Testing page (used only for internal testing) :
*  This allows a staff member to manually update the status of plates by inputting the plate_id and the new state.
![5.](https://github.com/karthik4j/Quick-Serve/blob/main/images/5.png?raw=true)
## Prototype website :
* The website allows end users to view the live count.
![4.](https://github.com/karthik4j/Quick-Serve/blob/main/images/4.png?raw=true)
