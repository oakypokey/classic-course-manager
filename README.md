[![Build Status](https://travis-ci.com/oakypokey/class2calendar.svg?branch=master)](https://travis-ci.com/oakypokey/class2calendar) [![Maintainability](https://api.codeclimate.com/v1/badges/e729cf9104fc94b462cc/maintainability)](https://codeclimate.com/github/oakypokey/class2calendar/maintainability)

### (Classy 2.0? CRN2Calendar? I don't know what to call this)

# Classic Course Manager (?)

## APIs

### Auth0 Identity Management

In order to be able to create your own instance of this application, you will need to create an Auth0 account and configure Google Social Sign-in using their steps. More information can be found [here](https://auth0.com/docs/connections/social/google).

_Ensure that the calendar scope is selected in scopes requested in your Auth0 Google Sign-in configuration_

When done, add your Auth0 Client ID and secret to your `.env` app like below:

```
AUTH0_CLIENT_ID=<YOUR AUTH0 CLIENT ID>
AUTH0_CLIENT_SECRET=<YOUR AUTH0 CLIENT SECRET>
```

### Google Calendar API

You will need to create an application in the Google API dashboard and note down the Client ID and Secret (you may have already done this when configuring Auth0: make sure to use the same Google Client ID and Secret that you used to configure Auth0). Ensure that the full calendar scope is selected in scopes requested in your Google Application. This will allow us to add events to our user's calendar on their behalf.

You will also need to register for a Google API Key. This will enable your application to source event information from Georgetown's academic calendar. Add it to your `.env` file like below:

```
GOOGLE_API_KEY=<YOUR GOOGLE API KEY>
```

## Development

### To get started, setup the project using the steps below:

1. Fork and clone the project onto your computer
2. In the root of the project, run: `yarn install`
3. Create a Conda environment by using: `conda create -n classic-env`
4. Activate the conda environment using: `conda activate classic-env`
5. Install the python dependencies using: `pip install requirements.txt`

### To start development server

1. Create two terminal windows in the root of your project
2. At the root of your project, run `yarn start`. This will start the webpack development server for the React Frontend. You can navigate to this by going to [http://localhost:3000](http://localhost:3000). This page will automatically reload as you make edits.
3. In the other terminal, run `flask run`. This will start the api for our project.
4. (To see your changes, run yarn build and then navigate to [http://localhost:5000/login](http://localhost:5000/login). Alternatively, you can disable CORS in your application for live reloading development of the React app, but this is not advised.)

## Testing

To run tests for the different components of this project, use the following:

1. To run tests for the front end using `create-react-app`'s in-built testing suite, use `yarn test` in the root of the project.
2. To run tests for the back end using `pytest`, run `pytest` in the root directory.
3. Travis CI has been configured already for this project. If you have it enabled for your repo, it should automatically run.

## Deployment

In order to deploy the finished application, it is important to build the front end. This can be done using `yarn build` which will create a folder. Flask has been configured to use this as the route directory to serve the front-end application. You can use the associated `Profile` to deploy this project on [Heroku](https://dashboard.heroku.com)
