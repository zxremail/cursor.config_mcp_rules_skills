#!/usr/bin/env bash

if [[ -d projects/ ]]; then
    cp -a .gitignore.more_for_cursor         projects/.gitignore
fi

if [[ -d skills-cursor/ ]]; then
    cp -a .gitignore.more_for_cursor         skills-cursor/.gitignore
fi

