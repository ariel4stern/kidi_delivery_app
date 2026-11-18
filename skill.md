# Goal:
- Build a website app in HTML that will manage the backstage of my app: delivery_distribution.
- This app would be able to make Manually counting of cartoons and bags, convert the output to DataFrame and make allocation for each store number a driver by the functions in those files,
 after the allocation functions, the website will offer an option of download the final DataFrame result as Excel file to specific directory.


## Structure Of Landing Page:
### One main page with 3 tabs.
- first tab will be for the cartoons counting.
- second tab will handle the allocations functions.
- third tab will handle the final file download.

## Design:
### Colors:
- background: animated colors and flying dots of sunset vibe, I want the user will feel like the end of the day and the peace that exists in these moments.
- tabs: pleasant orange with black font.
- landing page: mix of pleasant orange,white,gentle red with black font.

### Tabs:
- Each tab will be shown all the time the web is open.
- Each tab will direct to landing page with his purpose below.

## Goals Of Each Tab:
### First tab:
- Will use the functions from 'e_dal_output_table.py' 
- First it will use get_all_rows_output() function, it will get list(dict(str,any)) with the numbers of today stores in column:'store_number'.
- It will show for each store number a row in the landing page, in this row should be a 2 cell to fill one for cartoons_count(integer)  and one for bags_count(integer).
- After all fields were done will pop uo a button in the bottom of this landing page to confirm and continue. 
- While the bottom will clicked you need to activate the function update_output_table(pd.DataFrame),
 the pd.DataFrame will be with fields:
- - store number : the store numbers you got from get_all_rows_output()
- - cartoons_count : count of cartoons + count of bags by each store number.
- - driver_id : None for this step.
- If the system get a list of dict with len > 1 you need to pop up a green success message to the user,
 it will say to user: 'Success You allow to move on', and then all cells will be unable to interact.

### Second Tab:
- d



