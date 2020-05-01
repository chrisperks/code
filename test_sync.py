import tempfile
from pathlib import Path
import shutil
from sync import sync, determine_actions, read_paths_and_hashes
import pytest

def create_files(files): 
    source = tempfile.mkdtemp()

    for key in files.keys(): 
        (Path(source) / key).write_text(files[key])

    return source

def test_file_hash_is_found():
    source = create_files({"my-file": "a handy file!"})
    hashes = read_paths_and_hashes(source)
    assert "my-file" in hashes.values()

    shutil.rmtree(source)

def test_file_hashes_are_found(): 
    
    files = {  "file-1": "Some content!", 
               "file-2" : "Other content"}

    source = create_files(files)
    hashes = read_paths_and_hashes(source)
    assert "file-1" in hashes.values()
    assert "file-2" in hashes.values()

    shutil.rmtree(source)

def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source = create_files({"my-file": "a handy file!"})
    dest = create_files({"another-file": "another handy file!"})

    src_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    
    actions = determine_actions(src_hashes, dest_hashes, source, dest)
    expected = [
        ('copy', Path(source + '/my-file'), Path(dest + '/my-file')),
        ('delete', dest, 'another-file')
    ]
    assert list(actions) == expected

def test_when_a_file_has_been_renamed_in_the_source():
    source = create_files({"my-file": "a handy file!"})
    dest = create_files({"another-file": "a handy file!"})

    src_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    
    actions = determine_actions(src_hashes, dest_hashes, source, dest)
    expected = [
        ('move', Path(dest + '/another-file'), Path(dest + '/my-file'))
    ]
    assert list(actions) == expected















    # src_hashes = {'hash1': 'fn1'}
    # dst_hashes = {'hash1': 'fn2'}
    # actions = determine_actions(src_hashes, dst_hashes, Path('/src'), Path('/dst'))
    # assert list(actions) == [('move', Path('/dst/fn2'), Path('/dst/fn1'))]