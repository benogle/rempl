'''
MIT License

Copyright (c) 2009 Ben Ogle

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
'''

'''
REMPL is a script that will push a local playlist (*.m3u or *.pls) 
to a remote WinAMP instance running the AjaxAMP plugin. This is 
useful for playlists specifying remote streams such as radio 
stations or playlists generated by a satchmo or zina installation.

Usage is simple:

rempl.py /path/to/playlist.pls

If you would like to enqueue the playlist instead of immediately playing 
the specified playlist, add the '-e' argument:

rempl.py -e /path/to/playlist.pls

You must edit the SERVER var to point to your AjaxAMP install.
'''


#the AjaxAMP server url; You will need to edit this!
SERVER = 'http://192.168.1.100:5151'



import sys, urllib, urllib2
import os, re

#regexs for pls parsing
SECTION_RE = re.compile(r'^\[(.+)\]$')
KV_RE = re.compile(r'^([a-zA-Z0-9]+)=(.+)$')


def pushplaylist(fname, enqueue):
    f = open(fname, 'r')
    return setplaylist(fname, f, enqueue)
    
    
def setplaylist(fname, f, enqueue):

    files = getfiles(fname, f)

    if files == None:
        return 'file parse error'
        
    cmd = 'playfile'
    if enqueue:
        cmd = 'enqueuefile'
        
    status = 'ok!'
    
    #for each entry, make a request. slow!!
    for fi in files:
        param = urllib.urlencode(fi)
        resp = urllib2.urlopen('%s/%s' % (SERVER, cmd), param)
        
        if cmd == 'playfile':
            cmd = 'enqueuefile'
            
        if resp.read() != '1' :
            status = 'error with enqueue!'
    
    return status


def getfiles(fname, f):
    '''
    figures out what kind of playlist, calls the right parse function, 
    returns the file data in a list of dicts:
    
    [
        { 'filename': 'firstsong.mp3', 'title': 'song title' },
        { 'filename': 'secondsong.mp3', 'title': 'song title' },
        { 'filename': 'thirdsong.mp3', 'title': 'song title' },
        ...
    ]
    '''
    
    #playlist parsers
    PARSERS = {
        'm3u': parsem3u,
        'pls': parsepls
    }
    
    ext = fname[-3:].lower()
    
    if PARSERS.has_key(ext):
        return PARSERS[ext](f)
    
    return None
    

############# M3U

def parsem3u(f):
    
    lines = getlines(f)

    files = []
    
    for i in range(len(lines)):
        if not lines[i].startswith('#'):
            
            fileinfo = {'filename': lines[i]}
            
            if lines[i-1].startswith('#EXTINF:'):
                fileinfo['title'] = getm3utitle(lines[i-1])
            
            files.append(fileinfo)
    
    return files
    
           

def getm3utitle(info):
    #slophack like crazy
    #return anything after the first comma of the '#EXTINF:...' line
    return ','.join(info.split(',')[1:])
    
############ PLS

def parsepls(f):
    
    files = None
    
    struc = parsepls_structure(f)
    
    if struc.has_key('playlist'):
        
        playl = struc['playlist']
        
        if playl.has_key('numberofentries'):
        
            files = []
            
            for i in range(1,int(playl['numberofentries']) + 1):
            
                fi = 'file%d' % i
                ti = 'title%d' % i
            
                filei = { 'filename': playl[fi] }
                if playl.has_key(ti):
                    filei['title'] = playl[ti]
                    
                files.append(filei)
                
    return files
    
    
def parsepls_structure(f):
    '''
    pls is basically an ini structure:
    
    [playlist]
    numberofentries=1
    file1=some/file.mp3
    title1=song title
    
    This will return a dict like:
    
    ret = { 
        'playlist': {
            'numberofentries':1,
            'file1': 'some/file.mp3',
            'title1': 'song title'
        }
    }
      
    '''
    lines = getlines(f)
    
    ret = {}
    cursect = None
    
    for l in lines:
        
        sect = SECTION_RE.match(l)
        kv = KV_RE.match(l)
        
        if sect:
            cursect = {'numberofentries': '0'}
            ret[sect.group(1).lower()] = cursect
            
        elif kv and cursect:
            cursect[kv.group(1).lower()] = kv.group(2)
            
    return ret
    
############ Util

def getlines(f):
    return [ x.strip() for x in f.readlines() if len(x.strip()) > 0 ]

############ MAIN, yo

def usage(name):
    print 
    print '%s <arg> <fname>' % (name)
    print 'options:'
    print ' -e : enqueue playlist (default action is to play immediately)'


if __name__ == '__main__':
    
    l = len(sys.argv)
    
    if l == 2: 
        print pushplaylist(sys.argv[1], False)
    
    #You should be using optargs. 
    #You should have an option to specify the server url.
    #If anyone besides ben actually uses this, you will.
    elif l == 3: 
        enq = sys.argv[1] == '-e'
        print pushplaylist(sys.argv[2], enq)
        
    else:
        usage(sys.argv[0])