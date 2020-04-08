[![Build Status](https://travis-ci.com/oakypokey/class2calendar.svg?branch=master)](https://travis-ci.com/oakypokey/class2calendar) [![Maintainability](https://api.codeclimate.com/v1/badges/e729cf9104fc94b462cc/maintainability)](https://codeclimate.com/github/oakypokey/class2calendar/maintainability)

### (Classy 2.0? CRN2Calendar? I don't know what to call this)
# Classic Course Manager (?)

## Development
### To get started, setup the project using the steps below:
1. Fork and clone the project onto your computer
2. In the root of the project, run:  `yarn install`
3. Create a Conda environment by using:  `conda create -n classic-env`
4. Activate the conda environment using:  `conda activate classic-env`
5. Install the python dependencies using:  `pip install api/requirements.txt`

### To start development server
1. Create two terminal windows in the root of your project
2. At the root of your project, run `yarn start`. This will start the webpack development server for the React Frontend. You can navigate to this by going to [http://localhost:3000](http://localhost:3000). This page will automatically reload as you make edits.
3. Switch into the api directory using `cd api` and run `flask run`. This will start the api for our project.

## Testing
To run tests for the different components of this project, use the following:
1. To run tests for the front end using `create-react-app`'s in-built testing suite, use `yarn test` in the root of the project.
2. To run tests for the back end using `pytest`, navigate to `/app` and run `pytest` in the directory.
3. Travis CI has been configured already for this project.

## Deployment
In order to deploy the finished application, it is important to build the front end. This can be done using `yarn build` which will create a folder. Flask has been configured to use this as the route directory to serve the front-end application. You can use the associated `Profile` to deploy this project on [Heroku](https://dashboard.heroku.com)