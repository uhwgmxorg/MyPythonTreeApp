# MyPythonTreeApp

A small Python GUI application built with **Tkinter**, allowing users to manage hierarchical tree data interactively. The tree data can be saved to and loaded from XML files, compatible with the original C# XML structure. Optionally, it supports switching between local file storage and a (placeholder) web service.

## Features

- Create and delete nodes and sub-nodes using a TreeView.
- Context menu for node manipulation (right-click on the TreeView).
- Double-click in-place editing of node labels.
- Drag & Drop to reorganize nodes visually, with a semi-transparent “ghost” window.
- Load and save data as XML files.
- Placeholder hooks for loading/saving from a web service.
- UI configuration persistence using JSON (`config.json`).
- Toggleable message boxes and configurable web service URL.
- Lightweight and fully local.

![img](https://github.com/uhwgmxorg/MyPythonTreeApp/blob/master/Doc/100_1.png)

## Requirements

- Python **3.10** or newer  
- **Tkinter** (usually included with Python’s standard library)

## For using with Web-Service if docker is installed

`docker run --name my-xml-service-container -p 3000:3000 -p 5432:5432 -e POSTGRES_USER=xml_user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mydb -d uhwgmxorg/my-xml-service-postgresql-docker-image:1.1.0`

## Run the application

python3 MyPythonTreeApp.py

