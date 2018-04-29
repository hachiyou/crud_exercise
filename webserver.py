import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from query import select_all_restaurant,
add_restaurant,
select_restaurant,
update_restaurant,
delete_restaurant


class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """DISPLAY HTML documents."""
        try:
            if self.path.endswith("/restaurant"):  # show all the restaurant
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                result = select_all_restaurant()

                output = ""
                output += "<head><body>"

                for rest in result:
                    output += "<b>%s</b><br>" % rest.name
                    output += "<a href='/%s/edit'>Edit</a><br>" % rest.id
                    output += "<a href='/%s/delete'>DELETE</a><br><br>" % rest.id  # noqa

                output += "<a href='new'>Create New Restaurant</a></body></head>"  # noqa

                self.wfile.write(output)
                return

            if self.path.endswith("/new"):  # show the creation page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = '''<head><body>
<form action='/new_done' enctype='multipart/form-data' method='post'>
<h2>A new restaurant has been built.<br>What is the restaurant name:</h2>
<input type='text' name='rname'><br>
<input type='submit' value='Submit'>
</form></body></html>'''  # noqa
                self.wfile.write(output)

                return

            if self.path.endswith("/edit"):  # show the edit page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                rest_id = self.path[1:len(self.path)-5]
                rest_name = select_restaurant(rest_id).name
                output = '''<head><body>
<form action='/%s/edit_done' enctype='multipart/form-data' method='post'>
<h2>%s</h2><h3>will change name to: </h3>
<input type='text' name='new_name'><br>
<input type='submit' value='Submit'>
</form></body></html> ''' % (rest_id, rest_name)  # noqa
                self.wfile.write(output)

            if self.path.endswith("/delete"):  # show the delete page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                rest_id = self.path[1:len(self.path)-7]
                rest_name = select_restaurant(rest_id).name

                output = '''<head><body>
<form action='/%s/delete_done' enctype='multipart/form-data'  method='post'>
<h2>%s</h2><h3>will be deleted from the database!!! </h3>
<input type='submit' value='Submit'></form>
<Button onclick='window.history.back()'>Cancel</button>
</body></html> ''' % (rest_id, rest_name)  # noqa
                self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File not found: %s.' % (self.path))

    def do_POST(self):
        """Perform updates to the database."""
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
            if self.path.endswith("/new_done"):  # Perform insertion and show completion page  # noqa
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    rest_name = fields.get('rname')[0]
                add_restaurant(rest_name)

                output = "<head><body>%s has been built!<br><br>" % rest_name

                output += "<a href='../restaurant'>Home</a></body></head>"

                self.wfile.write(output)

            if self.path.endswith("/edit_done"):  # Perform update and show completion page  # noqa
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    rest_name = fields.get('new_name')[0]

                rest_id = self.path[1:len(self.path)-10]

                old_name = update_restaurant(rest_id, rest_name)

                output = "<head><body>%s has been renamed to %s! <br><br>" % (old_name, rest_name)  # noqa

                output += "<a href='../restaurant'>Home</a></body></head>"
                self.wfile.write(output)

            if self.path.endswith("/delete_done"):  # Perform delete and show completion page  # noqa
                rest_id = self.path[1:len(self.path)-12]

                old_name = delete_restaurant(rest_id)

                output = "<head><body>%s went out of business.<br><br>" % old_name  # noqa

                output += "<a href='../restaurant'>Home</a></body></head>"

                self.wfile.write(output)
        except IOError:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print('Web server running on port %s.' % (port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered. stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()
