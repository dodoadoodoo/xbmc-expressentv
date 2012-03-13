# coding: latin-1                                                                                                      
import urllib2
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

from xml.dom.minidom import parse, parseString

import base64

CATEGORY_URL = "http://www.expressen.se/Handlers/WebTvHandler.ashx?id=8793&output=MenuOutput"
HANDLER_URL = "http://www.expressen.se/Handlers/WebTvHandler.ashx?id="

MAGIC_URLS = {"8877":"3644404&tab=1", "8878":"3644404&tab=0", "8769":"3644404&tab=2", "8773":"3644404&tab=3", "8794":"3643234&tab=0", "8927":"3643225&tab=0", "8930":"3643242&tab=0", "8826":"3644741&tab=0", "8831":"3643244&tab=0", "3646739":"3643244&tab=1", "8886":"3643350&tab=0", "8792":"3643267&tab=1", "8785":"3646139&tab=0", "8770":"3643354&tab=0", "8816":"3646457&tab=0", "8791":"3646457&tab=1", "8776":"3643288&tab=1", "8775":"3643288&tab=2", "8870":"3643288&tab=3", "8887":"3643334&tab=0", "8884":"3643334&tab=1", "8867":"3643323&tab=0", "8852":"3643337&tab=1", "8801":"3643333&tab=0", "8766":"3643338&tab=0", "8767":"3643341&tab=0", "8765":"3643347&tab=0", "3680616":"3688306&tab=0", "8778":"3643342&tab=0", "8782":"3643339&tab=0", "8768":"3643339&tab=1"} 


__settings__ = xbmcaddon.Addon(id='plugin.video.expressentv')

def list_categories():
    doc, state = load_xml(CATEGORY_URL)
    if doc and not state:
        add_posts("Sök", MODE + "search/", isFolder=True)
        for category in doc.getElementsByTagName("category"):
            title = get_node_value(category, "title").encode('utf_8')
            categoryid = get_node_value(category, "id").encode('utf_8')
            add_posts(title, MODE + "category/" + categoryid, isFolder=True)
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("Expressen TV","Site down")')
        else:
            xbmc.executebuiltin('Notification("Expressen TV","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def list_subcategories(cid):
    doc, state = load_xml(CATEGORY_URL)
    if doc and not state:
        add_posts("Sök", MODE + "search/", isFolder=True)
        for category in doc.getElementsByTagName("category"):
            categoryid = get_node_value(category, "id").encode('utf_8')
            if categoryid == cid:
                title = get_node_value(category, "title").encode('utf_8')
                add_posts(title, MODE + "items/" + categoryid, isFolder=True)
                subcategories = category.getElementsByTagName("subcategories")
                if subcategories != None and len(subcategories) > 0: 
                    for subcategory in subcategories[0].getElementsByTagName("subcategory"):
                        title = get_node_value(subcategory, "title").encode('utf_8')
                        categoryid = get_node_value(subcategory, "id").encode('utf_8')
                        add_posts(title, MODE + "items/" + categoryid, isFolder=True)
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("Expressen TV","Site down")')
        else:
            xbmc.executebuiltin('Notification("Expressen TV","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def list_menu():
    for magic in MAGIC_NUMBERS:
        url = HANDLER_URL + magic
        doc, state = load_xml(url)
        if doc and not state:
            for item in doc.getElementsByTagName("item"):
                title = get_node_value(item, "title").encode('utf_8')
                xmlurl = get_node_value(item, "xmlurl").encode('utf_8')
                add_posts(title, MODE + "list/" + base64.b64encode(xmlurl,"-_"), isFolder=True)
        else:
            if state == "site":
                xbmc.executebuiltin('Notification("Expressen TV","Site down")')
            else:
                xbmc.executebuiltin('Notification("Expressen TV","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def list_items(categoryid, extraparam = ''):
    if categoryid in MAGIC_URLS:
        categoryurl = HANDLER_URL + MAGIC_URLS[categoryid]
    else:
        categoryurl = HANDLER_URL + categoryid + extraparam
    categoryworker(categoryurl)

def categoryworker(url):
    doc, state = load_xml(url)
    if doc and not state:
        items = doc.getElementsByTagName("items")
        for item in items[0].getElementsByTagName("item"):
            title = get_node_value(item, "title").encode('utf_8')
            itemid = get_node_value(item, "id").encode('utf_8')
            thumbs = item.getElementsByTagName("thumbs")
            thumbUrl = ""
            maxSize = 0
            if thumbs != None and len(thumbs) > 0:
                for thumb in thumbs[0].getElementsByTagName("thumb"):
                    size = int(thumb.getAttribute("size"))
                    if size > maxSize:
                        thumbUrl = thumb.childNodes[0].data
                        maxSize = size
            add_posts(title, MODE + "/play/" + itemid, thumb=thumbUrl)
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("Expressen TV","Site down")')
        else:
            xbmc.executebuiltin('Notification("Expressen TV","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def play_clip(clipid):
    url = HANDLER_URL + clipid
    doc, state = load_xml(url)
    if doc and not state:
        root = doc.getElementsByTagName("root")[0]
        title = get_node_value(root, "title").encode('utf_8')
        description = get_node_value(root, "desc")
        if description == None:
            description = ""
        else:
            description = description.encode('utf_8')
        vurls = doc.getElementsByTagName("vurls")
        maxbitrate = 0
        url = ""
        for vurl in vurls[0].getElementsByTagName("vurl"):
            bitrate = int(vurl.getAttribute("bitrate"))
            if bitrate > maxbitrate:
                url = vurl.childNodes[0].data
                maxbitrate = bitrate
        parts = url.split("/")
        rtmpUrl = parts[0] + "/" + parts[1] + "/" + parts[2] + "/" + parts[3]
        playPath = ""
        for i in range(4, len(parts)):
            if playPath == "":
                playPath = parts[i]
            else:
                playPath = playPath + "/" + parts[i]
        url = rtmpUrl + " swfVfy=true swfUrl=http://www.expressen.se/Static/swf/ExpPlayer.swf app=" + parts[3] + " pageUrl=http://www.expressen.se playPath=" + playPath + " flashVer=LNX 11,1,102,62"
        listitem = xbmcgui.ListItem(label=title, path=url)
        xbmcplugin.setResolvedUrl(HANDLE, succeeded=True, listitem=listitem)  
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("Expressen TV","Site down")')
        else:
            xbmc.executebuiltin('Notification("Expressen TV","Malformed result")')


def add_posts(title, url, description='', thumb='', isPlayable='true', isFolder=False):
    if title == None:
        title = ""
    else:
        title = title.replace("\n", " ")
    if thumb == None:
        listitem=xbmcgui.ListItem(title)
    else:
        listitem=xbmcgui.ListItem(title, iconImage=thumb)        
    if  description == None:
        listitem.setInfo(type='video', infoLabels={'title': title})
    else:
        listitem.setInfo(type='video', infoLabels={'title': title, 'plotoutline': description})
    listitem.setProperty('IsPlayable', isPlayable)
    listitem.setPath(url)
    return xbmcplugin.addDirectoryItem(HANDLE, url=url, listitem=listitem, isFolder=isFolder)

def do_search():
    keyb = xbmc.Keyboard('', 'Search')
    keyb.doModal()
    if (keyb.isConfirmed()):
        search = keyb.getText()
        list_items("8773", "&search=" + search)


def get_node_value(parent, name, ns=""):
	if ns:
		if parent.getElementsByTagNameNS(ns, name) and \
			    parent.getElementsByTagNameNS(ns, name)[0].childNodes:
			return parent.getElementsByTagNameNS(ns, name)[0].childNodes[0].data
	else:
		if parent.getElementsByTagName(name) and \
			    parent.getElementsByTagName(name)[0].childNodes:
			return parent.getElementsByTagName(name)[0].childNodes[0].data
	return None

def load_xml(url):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        xbmc.log("plugin.video.expressentv: unable to load url: " + url)
        xbmc.log(str(e))
        return None, "site"
    xml = response.read()
    response.close()
    try:
        out = parseString(xml)
    except:
        xbmc.log("plugin.video.expressentv: malformed xml from url: " + url)
        return None, "xml"
    return out, None


if (__name__ == "__main__" ):
    MODE=sys.argv[0]
    HANDLE=int(sys.argv[1])
    modes = MODE.split('/')
    MODE = modes[0]+"/"+modes[1]+"/"+modes[2]+"/"
    activemode = modes[len(modes) - 2]
    itemid = modes[len(modes) - 1]
    
    if activemode == "category" :
        list_subcategories(itemid)
    elif activemode == "play":
        play_clip(itemid)
    elif activemode == "list":
        categoryworker(base64.b64decode(itemid,"-_"))
    elif activemode == "items":
        list_items(itemid)
    elif activemode == "search":
        do_search()
    else :
        list_categories()


