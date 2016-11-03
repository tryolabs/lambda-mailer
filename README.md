# Tryolabs Lambda mailer

Uses [Zappa](https://github.com/Miserlou/Zappa) to deploy a serverless endpoint that receives a JSON and sends an email to a destination address. Made to support contact forms in our static website.

## Setup

_Before you begin, make sure you have a valid AWS account and your [AWS credentials file](https://blogs.aws.amazon.com/security/post/Tx3D6U6WSFGOK2H/A-New-and-Standardized-Way-to-Manage-Credentials-in-the-AWS-SDKs) is properly installed._

Make sure you are in a virtualenv, and run:

```
$ pip install -r requirements.txt
$ zappa deploy dev
```

To redeploy:

    $ zappa update dev

To deploy the production version:

    $ zappa deploy prod


### Environment variables
In the `zappa_settings.json` file, you can edit the environment variables for `dev` and `prod`:

```javascript
{
    "dev": {
        ...
        "environment_variables": {
            "FROM_EMAIL": "alan@tryolabs.com",
            "DESTINATION_EMAIL": "alan@tryolabs.com"
        }
    },
    ...
}
```

## Testing

With [httpie](https://httpie.org/), invoke the endpoint0 with the `message.json` test file as payload:

    $ http <endpoint> < message.json


## License

Copyright (c) 2016 [Tryolabs](https://tryolabs.com).

Released under the MIT License (See LICENSE).
