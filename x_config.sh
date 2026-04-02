#!/usr/bin/env bash

mkdir projects
mkdir skills-cursor
mkdir plans

if [[ -d projects/ ]]; then
    cp -a .gitignore.more_for_cursor         projects/.gitignore
fi

if [[ -d skills-cursor/ ]]; then
    cp -a .gitignore.more_for_cursor         skills-cursor/.gitignore
fi

if [[ -d plans/ ]]; then
    cp -a .gitignore.more_for_cursor         plans/.gitignore
fi

