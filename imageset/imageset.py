# Copyright (c) 2015, Nate Stedman <nate@natestedman.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import argparse
import os
import pystache

version = "1.2"

def main():
    parser = argparse.ArgumentParser(description="Apply templates to files from Xcode imagesets",
                                     add_help=True, version=version)
    
    # generator arguments
    generator_group = parser.add_argument_group("Built-in Templates")
    
    generator_group.add_argument("--generate-swift-extension", dest='generate_swift_extension', action='store_true', default=False,
                                 help="Generate a Swift extension on the image class with functions returning image objects.")
    generator_group.add_argument("--generate-objc-category", dest='generate_objc_category', action='store_true', default=False,
                                 help="Generate an Objective-C category on the image class with messages returning image objects.")
    
    generator_group.add_argument("--generate-swift-functions", dest='generate_swift_functions', action='store_true', default=False,
                                 help="Generate a Swift file of functions returning image objects")
    generator_group.add_argument("--generate-objc-functions", dest='generate_objc_functions', action='store_true', default=False,
                                 help="Generate an Objective-C header and implementation file of functions returning image objects")
    
    generator_group.add_argument("--generate-swift-constants", dest='generate_swift_constants', action='store_true', default=False,
                                 help="Generate a Swift file of String constants for each image name")
    generator_group.add_argument("--generate-objc-constants", dest='generate_objc_constants', action='store_true', default=False,
                                 help="Generate a Objective-C header and implementation file of NSString constants for each image name")
                                 
    # templates
    template_group = parser.add_argument_group("Custom Templates")
    
    template_group.add_argument("--template", dest='template', action='append',
                                 help="Adds a template file to process.")
    template_group.add_argument("--template-argument", dest='template_argument', action='append',
                                help="Adds an argument that will be passed to templates. Use the format arg=value")
    
    # customizing rendering
    customizing_group = parser.add_argument_group("Customizing Rendering")
    
    customizing_group.add_argument("--prefix", dest='prefix', action='store',
                                   help="The prefix to use in templates, which will be placed before all function, class, and constant names.")
    customizing_group.add_argument("--function-prefix", dest='function_prefix', action='store',
                                   help="The function prefix to use in templates. This works alongside the --prefix option, so do not include the prefix if that option is used. The default function prefix is the name of the imageset file.")
    customizing_group.add_argument("--constant-prefix", dest='constant_prefix', action='store',
                                   help="The constant prefix to use in templates. This works alongside the --prefix option, so do not include the prefix if that option is used. The default constant prefix is the name of the imageset file.")
    customizing_group.add_argument("--class-name", dest='class_name', action='store',
                                   help="The class name to use in templates. This works alongside the --prefix option, so do not include the prefix if that option is used. The default class name is the name of the imageset file.")
    customizing_group.add_argument("--swift-optionals", dest='swift_optionals', action='store_true', default=False,
                                   help="If this option is set, Swift functions will return optional images. If not, they will be force unwrapped.")
    
    
    # input
    input_group = parser.add_argument_group("Input")
    
    input_group.add_argument("--input", dest='imageset_filename', action='store', required=True,
                             help="The imageset directory to process.")
                                 
    # output
    output_group = parser.add_argument_group("Output")
    
    output_group.add_argument("--output", dest='output_directory', action='store', required=True,
                              help="The directory to output generated files to.")
    output_group.add_argument("--platform", dest="platform", action="store", required=True, choices=["osx", "ios"],
                              help="Determines if we're using UIImage or NSImage.")
                      
    # parse           
    results = parser.parse_args()
    image_class = "UIImage" if results.platform == "ios" else "NSImage"
    
    # use the images file name as the class name if one wasn't specified
    class_name = results.class_name
    
    if class_name is None:
        class_name = filename_without_extension(results.imageset_filename)
    
    # grab templates
    templates = results.template if results.template else []
    templates = map(lambda path: (path, (filename_without_extension(path)), templates), templates)
    
    # add built-in templates if requested
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    def add_builtin(path, name):
        templates.append((os.path.join(templates_dir, path), name))
    
    if results.generate_swift_extension:
        add_builtin("SwiftExtension.swift.mustache", "{0}+{1}.swift".format(image_class, class_name))
        
    if results.generate_swift_functions:
        add_builtin("SwiftFunctions.swift.mustache", "{0}{1}Functions.swift".format(none_to_empty(results.prefix), class_name))
    
    if results.generate_swift_constants:
        add_builtin("SwiftConstants.swift.mustache", "{0}{1}Constants.swift".format(none_to_empty(results.prefix), class_name))
    
    if results.generate_objc_category:
        add_builtin("ObjCCategory.h.mustache", "{0}+{1}.h".format(image_class, class_name))
        add_builtin("ObjCCategory.m.mustache", "{0}+{1}.m".format(image_class, class_name))
        
    if results.generate_objc_functions:
        add_builtin("ObjCFunctions.h.mustache", "{0}{1}Functions.h".format(none_to_empty(results.prefix), class_name))
        add_builtin("ObjCFunctions.m.mustache", "{0}{1}Functions.m".format(none_to_empty(results.prefix), class_name))
    
    if results.generate_objc_constants:
        add_builtin("ObjCConstants.h.mustache", "{0}{1}Constants.h".format(none_to_empty(results.prefix), class_name))
        add_builtin("ObjCConstants.m.mustache", "{0}{1}Constants.m".format(none_to_empty(results.prefix), class_name))
    
    template_arguments = map(lambda arg: arg.split('='), results.template_argument) if results.template_argument else []
    template_arguments = filter(lambda arg: len(arg) == 2, template_arguments)
    
    generate(results.imageset_filename,
             results.output_directory,
             templates,
             template_arguments,
             image_class,
             results.prefix,
             results.function_prefix,
             results.constant_prefix,
             class_name,
             results.swift_optionals)

def none_to_empty(string):
    return "" if string is None else string

def filename_without_extension(filename):
    return os.path.splitext(os.path.basename(os.path.normpath(filename)))[0]

def imagemap_images(imageset_filename):
    images = os.listdir(imageset_filename)
    images = filter(lambda name: name.endswith(".imageset"), images)
    images = map(lambda name: os.path.splitext(name)[0], images)
    return images

def view_for_image(image_name):
    return {
        "name": image_name,
        "selector-name": image_name[:1].lower() + image_name[1:]
    }
    
def parse_template_file(template_filename):
    with open(template_filename, 'r') as file:
        return pystache.parse(unicode(file.read()))

def generate(imageset_filename,
             output,
             templates,
             template_arguments,
             image_class,
             prefix,
             function_prefix,
             constant_prefix,
             class_name,
             swift_optionals):
    images = imagemap_images(imageset_filename)
    
    # view for templates
    view = {
        "prefix": prefix,
        "prefix-lowercase": prefix.lower() if prefix is not None else None,
        "function-prefix": function_prefix,
        "constant-prefix": constant_prefix,
        "class-name": class_name,
        "image-class": image_class,
        "swift-optionals": swift_optionals,
        "images": map(view_for_image, images)
    }
    
    for arg in template_arguments:
        view[arg[0]] = arg[1]
    
    # pre-parse templates
    parsed_templates = { t[1]: parse_template_file(t[0]) for t in templates }
    
    # render!
    renderer = pystache.Renderer()
    
    for filename, template in parsed_templates.iteritems():
        output_filename = os.path.join(os.path.abspath(output), filename)
        
        print "Rendering", output_filename
        
        view["filename-without-extension"] = filename_without_extension(output_filename)
        
        rendered = renderer.render(template, view)
        
        with open(output_filename, "w") as file:
            file.write(rendered)
