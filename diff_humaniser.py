import sys
import subprocess

def is_git_start(text):
    return text.startswith("diff --git")

def extract_changed_file(line):
    return list(set(line.replace("diff --git a/", "", 1).replace(" b/", " ", 1).split()))[0]

def extract_line_number(line):
    line_numbers = line.replace("@@", "", 1).split("@@")[0].strip().split()
    return {
        "-": int(line_numbers[0].split(",")[0].replace("-", "", 1)),
        "+": int(line_numbers[1].split(",")[0].replace("+", "", 1))
    }

def load_diff(file, git_root):
    diff_list = {}
    current_file = ""
    changes = []
    line_number = {}

    with open(file) as f:
        lines = f.readlines()
        line_number = {"-": -1, "+": -1}

        for line in lines:
            if is_git_start(line):
                if current_file != "":
                    diff_list[current_file] = changes
                    changes = []
                current_file = extract_changed_file(line)
            elif current_file != "" and not (line.startswith("index ") and ".." in line):
                if line.startswith("@@"):
                    changes.append("@@@@ " + line.split("@@", 2)[2].strip())
                    line_number = extract_line_number(line)
                elif not (line.startswith("---") or line.startswith("+++")):
                    if line.startswith("-"):
                        changes.append("-" + str(line_number["-"]) + " " + line.replace("-", "", 1))
                        line_number["-"] = line_number["-"] + 1
                    elif line.startswith("+"):
                        changes.append("+" + str(line_number["+"]) + " " + line.replace("+", "", 1))
                        line_number["+"] = line_number["+"] + 1
                    else:
                        changes.append(str(line_number["+"]) + line)
                        line_number["-"] = line_number["-"] + 1
                        line_number["+"] = line_number["+"] + 1
                elif (line.startswith("---") or line.startswith("+++")):
                    changes.append(line)

    return diff_list

def read_file(file_path):
    f = open(file_path)
    text = f.read()
    f.close()
    return text

def make_header(from_ver, to_ver, repo_name):
    return read_file("header.html").replace("""{{title}}""", repo_name).replace("""{{from}}""", from_ver).replace("""{{to}}""", to_ver)

def make_head(repo_name):
    return read_file("head.html").replace("""{{title}}""", repo_name)

def make_footer():
    return read_file("footer.html")

def make_html_file(html_body, body_header, repo_name):
    return "<html>" + make_head(repo_name) + "\n\t<body>" + body_header + "\n\t\t<div class='content'>" + html_body + "\n\t\t</div>\n\t"+make_footer()+"\n\t</body></html>"

def get_folder(file_path):
    return file_path.split("/")[0]

def get_file_name(file_path):
    if "/" in file_path:
        return file_path.split("/")[-1]
    return file_path

def make_menu_item(filename, current_folder, counter):
    html_menu = ""
    if(current_folder != get_folder(filename)):
        if current_folder != "":
            html_menu = html_menu + "\n\t\t\t</ul>"
        html_menu = html_menu + "\n\t\t\t<div onclick='toggleCollapsed(\""+get_folder(filename)+"\", this)'><a href='javascript:void(0)'>(+) " + get_folder(filename) + "/</a></div>"
        html_menu = html_menu + "\n\t\t\t<ul id='list_"+get_folder(filename)+"' style='display:none;'>"
    html_menu = html_menu + "\n\t\t\t\t<li><a href='#"+str(counter)+"'>" + filename + "</a></li>"

    return html_menu

def make_collapse_script():
    return """
        <script>
            var toggleCollapsed = function(folderName, clickedElement){
                var element = document.getElementById("list_" + folderName);
                if(element.style.display === "none"){
                    element.style.display = "block"
                    clickedElement.getElementsByTagName("a")[0].innerHTML = "(-) " + folderName
                }
                else{
                    element.style.display = "none"
                    clickedElement.getElementsByTagName("a")[0].innerHTML = "(+) " + folderName
                }
            }
        </script>
    """
def generate_diff(from_revision, to_revision, working_directory, output):
    output_file = open(output, "w")
    p = subprocess.Popen(["git", "diff", from_revision, to_revision], cwd=working_directory, stdout=output_file)
    p.wait()
    output_file.close()
    # os.system("git diff " + from_revision + " " + to_revision " > " + output)


if __name__ == '__main__':
    git_repo = "C:/Games/Steam/steamapps/common/Stellaris/"
    output = "diff.html"
    output_diff = "diff.txt"
    from_ver = "1.1.0"
    to_ver = "1.2.0"
    from_rev = "HEAD~1"
    to_rev = "HEAD"
    git_repo_title = "Comparison"

    if len(sys.argv) > 3:
        from_ver = sys.argv[1]
        to_ver = sys.argv[2]
        git_repo = sys.argv[3]
        output = from_ver + "_to_" + to_ver + ".html"
        output_diff = from_ver + "_to_" + to_ver + ".txt"
    else:
        print "Wrong syntax! Usage:"
        print "\tpython " + sys.argv[0] + " <from_version> <to_version> <path_to_git_repo> [repository_name] [from_revision] [to_revision]"
        print "'from' and 'to' revisions are optional. If not provided it will use HEAD~1 and HEAD"
        sys.exit(1)

    if len(sys.argv) > 4:
        git_repo_title = sys.argv[4]
    if len(sys.argv) > 6:
        from_rev = sys.argv[5]
        to_rev = sys.argv[6]

    print "Using git repo: " + git_repo
    print "From Revision: " + from_rev
    print "To Revision: " + to_rev

    generate_diff(from_rev, to_rev, git_repo, output_diff)

    diff_set = load_diff(output_diff, git_repo)

    html_table = ""
    html_menu = "\n\t\t<div class='menu' name='top'>"
    html_menu = html_menu + "<a href="+get_file_name(output_diff)+">(See raw diff)</a>"
    html_menu = html_menu + "\n\t\t\t<h1>Changed files:</h1>"
    current_folder = ""
    file_counter = 0

    for filename, change_list in sorted(diff_set.iteritems()):
        file_counter = file_counter+1
        html_menu = html_menu + make_menu_item(filename, current_folder, file_counter)
        current_folder = get_folder(filename)

        html_table = html_table + "\n\t\t\t<h1 class='title'><a name='"+str(file_counter)+"'>Changes for " + filename + " <small><a href='#top'>(scroll to top)</a></small></h1>"
        html_table = html_table + "\n\t\t<div class='file-change-block'>"
        for change in change_list:
            if change.startswith("@@@@"):
                html_table = html_table + "<hr/>"
                html_table = html_table + "<pre>"+change.strip("@@@@").strip() + "</pre>"
                html_table = html_table + "<pre>...</pre>"
            elif change.startswith("---"):
                html_table = html_table + "\n\t\t\t\t<pre class='before'><b>Old File:</b> " + change.replace("---", "", 1).replace("b/", "", 1).replace("a/", "", 1) + "</pre>"
            elif change.startswith("+++"):
                html_table = html_table + "\n\t\t\t\t<pre class='after'><b>New File:</b> " + change.replace("+++", "", 1).replace("b/", "", 1).replace("a/", "", 1) + "</pre>"
            elif change.startswith("-"):
                html_table = html_table + "\n\t\t\t\t<pre class='before'>" + change.replace("-", "", 1) + "</pre>"
            elif change.startswith("+"):
                html_table = html_table + "\n\t\t\t\t<pre class='after'>" + change.replace("+", "", 1) + "</pre>"
            else:
                html_table = html_table + "\n\t\t\t\t<pre>" + change + "</pre>"
        html_table = html_table + "\n\t\t</div>"
        html_table = html_table + "\n\t\t<div class='end-of-change'><a href='#"+str(file_counter)+"'>(scroll to start of changes)</a> <a href='#top'>(scroll to top)</a></div>"

    html_menu = html_menu + "\n\t\t\t</ul>"
    html_menu = html_menu + "\n\t\t</div>"

    f = open(output, 'w')
    f.write(make_html_file(html_menu+html_table+make_collapse_script(), make_header(from_ver, to_ver, git_repo_title), git_repo_title))
    f.close()
