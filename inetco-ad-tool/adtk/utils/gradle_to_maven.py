'''
Current state of project

This project is an incomplete 
'''

import argparse
import re
import os
import pyperclip

class Dependency:
    def __init__(self, group=None, artifact=None, version=None, path=None):
        self.group = group
        self.artifact = artifact
        self.version = version
        self.path = path

    def as_maven(self):
        _maven_parts = []

        if self.group:
            _group_part = "<groupId>{}</groupId>".format(self.group)
            _maven_parts.append(_group_part)

        if self.artifact:
            _artifact_part = "<artifactId>{}</artifactId>".format(self.artifact)
            _maven_parts.append(_artifact_part)

        if self.version:
            _version_part = "<version>{}</version>".format(self.version)
            _maven_parts.append(_version_part)

        if self.path:
            _scope_part = "<scope>system</scope>"
            _path_part = "<systemPath>{}</systemPath>".format(self.path)
            _maven_parts.append(_scope_part)
            _maven_parts.append(_path_part)

        # join parts with new lines, and add tab indentation before each line
        _joined_parts = "\n".join(map(lambda x: "\t" + x, _maven_parts))
        return "<dependency>\n{}\n</dependency>".format(_joined_parts)

def parse_dependency(s):
    try:
        # Repository dependency
        if re.search("compile(?:\s*)[\"\'].*?[\"\']", s):
            group, artifact, version = re.search("[\"\'](.*):(.*):(.*)[\"\']", s).groups()
            return Dependency(group, artifact, version)

        # System dependency
        elif re.search("compile files", s):
            assert s.find(',') == -1, "Unimplemented parsing of multiple files with 'compile files'"
            path = re.search("\([\"\'](.*)[\"\']\)", s).group(1)
            return Dependency(path=path)

        # Treating this as a repository dependency
        elif re.search("testCompile", s):
            group, artifact, version = re.search("[\"\'](.*):(.*):(.*)[\"\']", s).groups()
            return Dependency(group, artifact, version)

    except Exception as e:
        print()
        print("ERROR: Failed to parse:", s)
        print("Poorly formatted string or case unimplemented")
        print("Skipping...")
        print()

    return None

def main():
    # parse input args
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Gradle File", type=str)
    parser.add_argument("-c", "--copy", help="Copy to Clipboard", action="store_true")
    args = parser.parse_args()

    # quick sanity check file path exists
    assert os.path.exists(args.infile), "File path not found"

    with open(args.infile, 'r') as f:
        file_contents = f.read()

        # find where dependencies start in document
        match = re.search("\sdependencies(?:\s*){", file_contents)
        assert match, "Dependency section in gradle file not found"

        # find where dependencies end
        dependency_start_idx = match.end(0)
        dependency_end_idx = -1
        open_bracket_count = 1
        close_bracket_count = 0
        for idx, c in enumerate(file_contents[dependency_start_idx:]):
            if c == '}':
                close_bracket_count += 1
            elif c == '{':
                open_bracket_count += 1

            if close_bracket_count == open_bracket_count:
                dependency_end_idx = dependency_start_idx + idx
                break

        assert dependency_end_idx != -1, "Could not find closing brace of dependency section in gradle file"
        dependency_section = file_contents[dependency_start_idx:dependency_end_idx]

        # Parse dependencies
        _dependencies = []
        for row in dependency_section.split('\n'):
            try:
                _dependency = parse_dependency(row)
                if _dependency:
                    _dependencies.append(_dependency)
            except:
                pass

    output = '\n\n'.join(map(Dependency.as_maven, _dependencies))

    # Output
    print("#################################")
    print(output)
    print("#################################")
    if args.copy:
        pyperclip.copy(output)
        print()
        print("Successfully Copied to Clipboard!")