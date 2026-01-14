import os


def read_file(filename):
    with open(filename, encoding='utf8') as file_:
        return file_.read()


def write_to_file(filename, content, mode='w'):
    with open(filename, mode, encoding='utf8') as file_:
        return file_.write(content)


def render_template(output_path, context):
    template_path = os.path.join(os.getcwd())
    content = read_file(template_path)

    for key, value in context.items():
        content = content.replace('{%s}' % key, str(value))

    write_to_file(output_path, content)
