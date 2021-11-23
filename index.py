import os, re,  traceback
from pathlib import Path
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader,  select_autoescape, PackageLoader
from markdown2 import markdown
from playsound import playsound #handy if you want a dink when site updates
####
from graphdb import GraphDB #https://github.com/CodyKochmann/graphdb
db = GraphDB('db/graph.db') 
####
from config import config


env = Environment(loader=FileSystemLoader('/Library/WebServer/Documents/case-studies/templates/'))
site_location = '/Library/WebServer/Documents'
watch_folder = '/Library/WebServer/Documents/case-studies/docs'
output_folder = '/Library/WebServer/Documents/case-studies/docs'
basepath = Path( watch_folder )
unique_tags = []
POSTS = {}  ## READ IN THE MARKDOWN FILES, PUT THE HTML IN
FILES = {}  ## USE A SEPARATE OBJ TO STORE WHERE THE FILES ARE, sigh!

def doSomethingWithFile(f):
    if f.endswith(".md"):
        
        with open(f, 'r') as file:
            POSTS[file.name] = markdown(file.read(), extras=['metadata'])
            #print("FILE:", f)
            FILES[file.name] = f
            #POSTS[file.name]['path'] = f

def doSomewthingWithDir(folder):
    ''
    #print("FOLDER:", folder)   



def render():
    print("rendering all in:", watch_folder)
    try:
        
        ####### READ IN THE WATCH FOLDER ######

        for root, dirs, files in os.walk(watch_folder):
            for filename in files:
                doSomethingWithFile(os.path.join(root, filename))

            for dirname in dirs:
                doSomewthingWithDir(os.path.join(root, dirname))

            
        ####### END READ IN THE WATCH FOLDER - ADD THE DEFAULTS
        for post in POSTS:
            
            p = FILES[post].replace(".md", ".html")
            POSTS[post].metadata['path'] = p # A file path for writing the html
            folderpath = os.path.dirname(p)
            POSTS[post].metadata['folderpath']  = folderpath

            if 'title' not in POSTS[post].metadata:
                title = post.replace( folderpath, "")
                title = title.replace( "/", "")
                title = title.replace( ".md", "")
                POSTS[post].metadata['title'] = title

            if 'tags' not in POSTS[post].metadata:
                POSTS[post].metadata['tags'] =''
            if 'thumbnail' not in POSTS[post].metadata: 
                # is there a thumbnail graphic in this folder?
                POSTS[post].metadata['thumbnail'] ='/site/assets/thumbnail.jpg'
            else:
                path = folderpath.replace(site_location, "")
                POSTS[post].metadata['thumbnail'] = path + "/"+ POSTS[post].metadata['thumbnail']
            if 'summary' not in POSTS[post].metadata: 
                # is there a thumbnail graphic in this folder?
                POSTS[post].metadata['summary'] =''

            try:
                POSTS[post].metadata['date'] = datetime.strptime(POSTS[post].metadata['date'], '%Y-%m-%d' )
            except: # hack, use now if it doesn't have a date
                now = datetime.now()
                POSTS[post].metadata['date'] = str( now.strftime("%Y"))

            POSTS[post].metadata['sitefolderpath']  = folderpath.replace(site_location, "") +"/"
            p = p.replace(site_location, "")
            POSTS[post].metadata['sitepath'] = p # A relative path for the web page

        ########################## END POSTS ######################################

        home_template = env.get_template('home.html')
        post_template = env.get_template('post.html')
        tags_template = env.get_template('tags.html')
        posts_metadata = []

        for post in POSTS:
            post_metadata = POSTS[post].metadata
            if 'index' in post_metadata:
                shouldIndex = post_metadata['index']
                if shouldIndex.lower() == 'false'  :
                    '' # DON'T ADD ME
                else:
                    posts_metadata.append( post_metadata )
            else: #they haven't mentioned it, so publish to index.html
                posts_metadata.append( post_metadata )

        tags = [post['tags'] for post in posts_metadata]
        
        for tag in tags:
            this_tags = tag.split(",")
            for this_tag in this_tags:
                trimmed_tag = this_tag.strip()

                if trimmed_tag not in unique_tags and trimmed_tag != " " and trimmed_tag != '':
                    unique_tags.append( trimmed_tag )
        unique_tags.sort()

        # INDEX
        home_html = home_template.render(posts=posts_metadata, tags=tags, unique_tags=unique_tags, config=config)
        with open(output_folder+'/index.html', 'w') as file:
            print("Writing index:",output_folder+'/index.html' )
            file.write(home_html)
               
        i = 0
        for post in POSTS:
            # https://github.com/trentm/python-markdown2/wiki/metadata
            post_metadata = POSTS[post].metadata

            post_data = {
                'content': POSTS[post],
                'title': post_metadata['title'],
                'date': post_metadata['date'],
                'thumbnail':post_metadata['thumbnail'],
                'tags': post_metadata['tags'].split(","),
                'summary':post_metadata['summary'],
                'path':post_metadata['path']
        
            }

            #replace .md with .html so the links work
            content = POSTS[ post ]
            new_content = re.sub('\.md','.html',content)
            post_data['content'] = new_content
            #post_data['path'] = FILES[post].replace(".md", ".html")

            #index the text

            #build the a-to-z

            post_html = post_template.render(post=post_data,  config=config)
            # save the file to the same place as the .md file it came from

            #post_file_path = output_folder+'/posts/{slug}.html'.format(slug=post_metadata['slug'])
            post_file_path = post_data['path']
            os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
            with open(post_file_path, 'w') as file:
                file.write(post_html)
                i = i +1
            #playsound("assets/ding.wav")

                # TAGS
        tags_html = tags_template.render(posts=posts_metadata, tags=tags, unique_tags=unique_tags,  config=config)

        with open(output_folder+'/tags.html', 'w') as file:
            print("Writing tags:",output_folder+'/tags.html' )
            file.write(tags_html)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        print(i, "files updated", dt_string)


    except Exception as inst:
        print(inst)
        traceback.print_exc()
        playsound("assets/error.wav")# How many times does this bomb and I don't know? 


if __name__== '__main__':
    render()


'''
# NOT IMPLEMENTED YET BUT WANT TO MAKE A GRAPH OF CONTENT
for a in range(10):
   ...:     b = a + 1
   ...:     print(a, b)
   ...:     db.store_relation(a, 'related to', b)
   '''