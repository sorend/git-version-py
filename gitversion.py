#!/usr/bin/env python

import subprocess
import semantic_version
import re
import argparse


BASE_VERSION_STRING = "0.0.0"
BASE_VERSION = semantic_version.Version(BASE_VERSION_STRING)


def git(*args):
    cmd_line = ["git"] + list(args)
    return subprocess.check_output(cmd_line, text=True).strip().splitlines()


def tags_by_branch(branch):
    return git("tag", "--merged", branch)


def current_branch_or_tag():
    try:
        return git("symbolic-ref", "--short", "HEAD")[0]
    except:
        return git("describe", "--tags")[0]


def current_commit_hash():
    return git("rev-parse", "--verify", "HEAD", "--short")[0].rjust(7, '0')


def commits_distance(tag=None):
    if tag is None:
        return git("rev-list", "--count", "HEAD")[0]
    else:
        return git("rev-list", "--count", "HEAD", f"^{tag}")[0]


def get_commits_since(tag=None):
    try:
        if tag is not None and len(git("tag", "-l", tag)) > 0:
            last_commit = git("show-ref", "-s", tag)[0]
            return git("log", "--pretty=%B", f"{last_commit}..HEAD")
        else:
            return git("log", "--pretty=%B", "HEAD")
    except:
        return []  # no commits


def get_previous_tag_and_version():
    cb = current_branch_or_tag()
    branch_tags = tags_by_branch(cb)
    previous_version = BASE_VERSION
    previous_tag = None
    
    for tag in branch_tags:
        try:
            tag_without_prefix = tag.lstrip('v')  # remove "v" from "v1.2.3" -> "1.2.3"
            v : Version = semantic_version.Version(tag_without_prefix)
            if len(v.prerelease) > 0:
                continue
            elif previous_version < v:
                previous_version = v
                previous_tag = tag
        except:
            pass
                
    return previous_tag, previous_version


def get_new_version():
    pt, pv = get_previous_tag_and_version()
    
    previous_version = semantic_version.Version(major=pv.major, minor=pv.minor, patch=pv.patch + 1)

    cb = current_branch_or_tag()

    if cb != "main":
        branch_sanitized_name = re.sub(r"[^a-z0-9]", "", cb.lower())[:20]
        prerelease = [branch_sanitized_name, commits_distance(pv), current_commit_hash()]
        previous_version = semantic_version.Version(major=previous_version.major, minor=previous_version.minor, patch=previous_version.patch, prerelease=prerelease)

    return str(previous_version)


def get_previous_version():
    pt, pv = get_previous_tag_and_version()
    return str(pv)


if __name__ == "__main__":

    print(get_previous_version())
    print(get_new_version())
    
        
