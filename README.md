[![Build Status](https://travis-ci.com/oakypokey/class2calendar.svg?branch=master)](https://travis-ci.com/oakypokey/class2calendar) [![Maintainability](https://api.codeclimate.com/v1/badges/e729cf9104fc94b462cc/maintainability)](https://codeclimate.com/github/oakypokey/class2calendar/maintainability)
# Class 2 Calendar




## Summary
This project provides a way for Georgetown University students to easily add classes to their Google Calendar with all of the information prepopulated.

Students can use either the 5-digit CRN associated with the course that they are taking, or the the course code and section (for example: OPIM 240 - 03) in order to select classes. After selection, students will be able to log into their google account and export their selections.

## Installation
1. Create a new Conda environment  and activate it
    ```
    conda create -n <NAME>
    conda activate <NAME>
    ```
2. Install the required packages
    ```
    pip install -r requirements.txt
    ```
3. Start the program using the following command
    ```    
    python app
    ```
4. If you would like to make any modifications and test for breaking changes, use the following command in the root directory
    ```
    pytest
    ```

## Screenshots

