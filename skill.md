# Goal:
- Build a main_app page that will include the all routers.
- Build a HTML page for each Tab. main_page should manage all HTML pages,
- Build one HTML page for the entering window with Welcome colors and design right in center of the Welcome page, with button for start process, this page
 will be able to navigate with the landing page(all tabs) and there will be options to return to the entering window.
- main_page should run as uvicorn website app ,that will manage the backstage of my app: delivery_distribution.
- This app would be able to make Manually counting of cartoons and bags,
- convert the output to DataFrame and make allocation for each store number a driver by the functions in those files, 
  after the allocation functions, the website will offer an option of download the final DataFrame result as Excel file.

## Structure Of Landing Page:
### One main page that will run these 4 tabs.
- before the first tab, put a button for the function update_driver_available_not(driver_id:int,able_str:str) from 'c_dal_drivers.py'
 it will pop up a list of all drivers and their status with get_drivers_name_ids_status()
 the user will be able to choose driver or more to convert his field to 'available'
 with update_driver_available_not function.
- also you need to put a button beside the first button in order to change the driver for specific point.
 there will be option to select only one point from today points to change his driver with
 update_day_point(d_id,day:get_current_day(),point) function from
 d_dal_points, after selection will pop up a list of all drivers each one with his name and id with get_drivers_name_ids() from c_dal_drivers.py,
- and don't forget to handle the confirmation with a confirmation button for each selection and status request details as message.
- last button before the first tab beside the previous button, put a 3 options button one for setting
 all driver count in driver table back to 0 with the function reset_cartoons_count() from
 'c_dal_drivers.py'. second option will be to refresh output_table_two with the function
 refresh_output_table_data() from 'eb_router_output_table_two.py'. the last option should be refresh output_table
 with function:refresh_output_table_data() from e_router_output_table.

- first tab will be for the cartoons counting.
- second tab will handle the final file download.
- third tab will have a several functions to manage our db. 

## Design:
### Colors:
- background: animated colors and flying dots of sunset vibe, I want the user will feel like the end of the day and the peace that exists in
  these moments.
- tabs: pleasant orange with black font.
- landing page: mix of pleasant orange,white,gentle red with black font.

### Tabs:
- Each tab will be shown all the time the web is open.
- Each tab will direct to landing page with scrolling if needed,
with his purpose below.
- Tab Names:
- - first  "Cartoons Counting"
- - second "Save and Print"
- - third  "Updating DataBase"

## Goals Of Each Tab:
### First tab:
- First it will use get_all_rows_output() function from 'e_dal_output_table.py', it will get list(dict(str,any)).
- It will show for each store number a row in the landing page, in this row should be 2 cell to fill,
 one for cartoons_count(integer)  and one for bags_count(integer). 

- if not all cells filled with values, the 'confirm and continue' button of
 all cells in the bottom need to be unable to click, if the user try to click should be shown an error message and redirect in the tab
 to the empty cell and in the message write "you must fill all cells if no cartoons left fill with 0."  
 
- After all fields were done will pop up a button in the bottom of this landing page to 'confirm and continue'. 
- While the bottom will clicked you need to activate the function counting_confirmation(dataframe: pd.DataFrame)
  from 'f_functions.py' the pd.DataFrame will be with fields:
- - store number : the store numbers you got from get_all_rows_output() in 'e_dal_output_table.py'
- - cartoons_count : count of cartoons + count of bags by each store number.
- - driver_id : None for this step.
- If the function counting_confirmation() return True you need to activate the function
 allocation_division_distribution_points(pd.DataFrame) from 'f_functions.py' on a DataFrame that you will get
 from the function convert_output_table_to_df() from 'f_functions.py'.
- If the function counting_confirmation() return False you should pop up a red error message to inform to user, what he was wrong in his steps.
- after the allocation from the confirmation you should pop up a green success message to the user,
 it will say to user: 'Success You allow to move on', in f_functions.py I added a new function
 insert_to_output_two_all_null() this function should be activated after,
 the confirmation and continue in tab1,all NAN value inserted to output_two table,
  also the DataFrame represented after the confirm and continue should include output_table_two and
 output_table to show all detailed and to be ready to download as Excel, with merged_output_tables()
 function from f_functions.py, and then all cells will be unable to interact.

### Second Tab:
- will be shown Dataframe that represented the output_table to see the result of the first tab(counting),
 with function convert_output_table_to_df() from 'f_functions.py'. 
- after the DataFrame will be 2 buttons under the center of the DataFrame,
 the first button will be used for downloading the file as Excel with function
 export_excel() from 'f_functions.py', the second will be for refreshing the DataFrame with the function:
 merged_output_tables() from f_functions.py.
 

### Third Tab:
- will show 1 option button, the user can decide what router functions to use from list of the routers.
- if the user choose a_router_store.py will be shown a new option button with all the related router functions.
- each option in the list is representing the options describe below.
 if its list(dicts)/dict - the output should be showing under the button as DataFrame,
 else - will be shown beside the options bar as message,
 if the function have hyperparameters you will need to pop up a cell beside the option bar,
 to fill a JSON/hyperparameters as the function required.
 after the user fill the required fields need to pop up confirmation button the move on the process.
- every function should inform the user about error/success with details after the confirm button will be clicked. 


- the function from 'eb_router_output_table.py': patch_output_two_data(output_number:int,output_data:PatchOutputDataTwo)
 need to have a unique button, if this button clicked will pop up an input cell to be filled by the user with instruction of data reception by the function requires but pay attention in the PatchOutputDataTwo fields leave only the
 output_number and driver_id number from PatchOutputDataTwo the store count will stay in db as it was before.
 The DataFrame details under this unique function must be relevant, use the function merged_output_tables() from 'f_funtions.py', and show the DataFrame all the time
 After any confirmation button was clicked refresh this DataFrame with this function merged_output_tables().
 also .
 
 

- from a_router_store.py -> functions: insert_store(store: Store),patch_store(store_number:int,update_store: StoreUpdate),delete_existing_store(store_number: int).
- from b_router_delivery.py -> functions: patch_existing_distribution_line(updating_distribution_line:PatchDistributionLine).
- from c_router_drivers.py -> functions: insert_new_driver(new_driver: NewDriver),patch_existing_driver(driver_id: int, driver: PatchDriver),delete_existing_driver(driver_id: int)
- from d_router_points.py -> functions: insert_point(p:Point),update_day_point(p:UpdatePoint),delete_point(day:str,point:int).
- from e_router_output_table.py -> functions: get_output_data(),insert_new_output_row(output_data:OutputData),patch_output_data(output_number,output_data:PatchOutputData),
 delete_output_data_by_number(output_number:int), refresh_output_table_data().
- from eb_router_output_table_two.py -> functions: patch_output_data(output_number,output_data:PatchOutputData),refresh_output_table_data()

### Specials:
- make upgrade for main_page to run the delivery app in public server.
- make the delivery app also adjusted for mobile phones.
- remove the bug after confirm of tab3 here is error: AttributeError: module 'eb_router_output_table_two' has no attribute 'PatchOutputData'
 find the bug in the code and let me know what to change in it. 

follow the instructions from skill.md pay attention to the Specials in the bottom of the page its very relevant,
look at the HTML pages and css/js files look for bugs and let me know how to fix,
if page require changes make the changes and send available version to download,
most important: 4 HTML pages, 1 style.css,1 common.js, and one main_page to manage all the db and routers and HTML pages.
make the welcome design as the tabs design. there is problem in tab3 in unique function ad write in skill.md files



