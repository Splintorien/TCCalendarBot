# TCAlendar

This project is greatly inspired from the ASTUSbot made for the TC discord server. Please go and see it [here](https://github.com/TCastus/ASTUSbot).

This bot is used in a Discord server to display the agenda of the TCA groups at the INSA (even though it can work with all groups).

## Requirements

This app can be deployed using Docker. To build the Docker image, run the following command:

```bash
docker build --tag tcalendar .
```

Then to lauch the simulation, run:

```bash
docker run -it --rm --env-file .env -v $PWD:/bot --name container-tcalendar tcalendar
```
