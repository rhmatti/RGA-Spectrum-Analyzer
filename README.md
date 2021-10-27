# RGA Spectrum Analyzer

Installation Instructions
--------------------
1. To run, users must have python version 3.9 or newer installed on their machine.

2. In addition to the base install of python, the following packages are required:

	a. Scipy
	
		python -m pip install scipy

	b. Numpy
	
		python -m pip install numpy

	c. Pillow
	
		python -m pip install pillow

	d. Matplotlib
	
		python -m pip install matplotlib
3. Download the code as a .zip file, and extract all contents to the desired directory


User Instructions
--------------------
1. Open the file "RGA Spectrum Analyzer.pyw"

2. Select the "Import" option from the File menu (File>Import) or use the shortcut `<Ctrl+I>`

3. Using the navigation window, navigate to an output file generated from the SRS RGA software (ending in .ana) and import it

4. Automatic Analysis:

	a. Select "Auto-Anayze" from the Analysis menu (Analysis>Auto-Analylze) or use the shortcut `<Ctrl+R>`
  
	b. A separate window will open with the results of the analysis
  
	c. The results will show the name of the gas, along with the partial pressure in Torr and % composition
  
	d. To save these results, click anywhere within the results window and use the `<Ctrl+S>` command
  
	e. The "Auto-Anayze" function searches for peak matches within a certain range of the expected mass (Δm)
	and above a certain pressure threshold (P_min) which can be adjusted in the "Settings" (File>Settings)

5. Select a desired plot type from the "Plot" menu:

	a. Single RGA Scan:
	* Plots one RGA scan at a single instance in time from the binary data file
	* Use the navigation controls to change which scan is plotted
    
	b. All RGA Scans:
	* Plots all of the RGA scans from the binary data file
    
	c. Total Pressure Change:
	* Plots the total pressure (sum of all partial pressures) as a function of time
    
	d. Partial Pressure Change:
	* Plots the partial pressure of a specific gas that the user selects from the submenu
	* The gases available for selection include: Methane, H_2O, Ne, N_2, NO, O_2, Ar, and CO_2

6. To save the graph on screen, use the save icon in the toolbar at the bottom of the screen,
	select "Save" from the drop-down File menu (File>Save), or use the shortcut `<Ctrl+S>`


