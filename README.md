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

## Depoloyment
In order to deploy the finished application, it is important to build the front end. This can be done using `yarn build` which will create a folder. This, build, is where you will be 


## Available Scripts (React)


### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.
