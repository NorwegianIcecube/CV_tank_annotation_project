import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import cv2

IMG_PATH = 'data/tank_video_frames'
ANNOTATION_PATH = 'data/auto_annotated'
EXPORT_PATH = 'data/fixed_annotated'
imscale = 1.0
# Create the window with size 1200x600
window = tk.Tk()

label_table = {
    '0': 'Leopard 2A4 PL',
    '1': 'M1A1 Abrams',
    '2': 'T-90M',
    '3': 'Unkown vehicle'
}

window.geometry('1500x900')

select_tool = True
draw_tool = False
delete = False

chosen_object = None

class AutoScrollbar(ttk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class TankObject:
    def __init__(self, label, points, first=False):
        self.label = label
        self.points = [Point(x, y, self) for x, y in zip(points[::2], points[1::2])]
        for point in self.points:
            point._get_neighbours(first)

    def scale_points(self, x, y, scale_x, scale_y):
        for point in self.points:
            point_x, point_y = point.get_coords()
            new_x = x + (point_x - x) * scale_x
            new_y = y + (point_y - y) * scale_y
            point.set_coords(new_x, new_y)
            
    def clear_points(self):
        for point in self.points:
            point._delete_line()
            image_window.delete(point.circle)

class Point:
    def __init__(self, x, y, parent):
        self.parent = parent
        self.x = x
        self.y = y
        self.left_neighbour = None
        self.right_neighbour = None
        self.first = False

    def _draw_line(self):
        self.current = tk.StringVar()
        self.current.set(image_window.create_line(self.x, self.y, self.right_neighbour.x, self.right_neighbour.y, fill='red', width=2))

    def _get_neighbours(self, first=False):
        if first:
            self.first = True
            return
        try:
            self.left_neighbour = self.parent.points[self.parent.points.index(self)-1]
        except IndexError:
            self.left_neighbour = self.parent.points[-1]
        try:    
            self.right_neighbour = self.parent.points[self.parent.points.index(self)+1]
        except IndexError:
            self.right_neighbour = self.parent.points[0]

        self._draw_line()

        self.circle = image_window.create_oval(self.x-3, self.y-3, self.x+3, self.y+3, fill='blue', outline='black', width=2)
        image_window.tag_bind(self.circle, '<Button-1>', self.button_1_modes)
        image_window.tag_bind(self.circle, '<B1-Motion>', self.drag_point)
        image_window.tag_bind(self.circle, '<ButtonRelease-1>', self.put_circle_on_top)

    def button_1_modes(self, event):
        if select_tool:
            self.display_class()
        elif draw_tool:
            if self.first:
                print("self.first")
        elif delete:
            self.delete_self(event)

    def set_coords(self, x, y):
        self.x = x
        self.y = y

    def get_coords(self):
        return self.x, self.y
        
    def drag_point(self, event):
        x = image_window.canvasx(event.x)
        y = image_window.canvasy(event.y)
        image_window.move(self.circle, x-self.x, y-self.y)
        self.set_coords(x, y)
        self._delete_line()
        self.left_neighbour._delete_line()
        self.current.set(image_window.create_line(self.x, self.y, self.right_neighbour.x, self.right_neighbour.y, fill='red', width=2))
        self.left_neighbour.current.set(image_window.create_line(self.left_neighbour.x, self.left_neighbour.y, self.x, self.y, fill='red', width=2))

    def put_circle_on_top(self, event):
        image_window.tag_raise(self.circle)
        image_window.tag_raise(self.left_neighbour.circle)
        image_window.tag_raise(self.right_neighbour.circle)


    def _delete_line(self):
        image_window.delete(self.current.get())

    def delete_self(self, event=None):
        if not delete:
            return
        self._delete_line()
        self.left_neighbour._delete_line()
        image_window.delete(self.circle)
        self.parent.points.remove(self)
        self.left_neighbour.right_neighbour = self.right_neighbour
        self.right_neighbour.left_neighbour = self.left_neighbour
        self.left_neighbour._draw_line()
        image_window.tag_raise(self.left_neighbour.circle)
        image_window.tag_raise(self.right_neighbour.circle)

    def display_class(self):
        global chosen_object
        chosen_object = self.parent
        label_var.set(label_table[self.parent.label])
        
def fn_select_tool():
    global select_tool
    select_tool = True
    global draw_tool
    draw_tool = False
    global delete
    delete = False
    global is_drawing
    is_drawing = False

def fn_draw_tool():
    global draw_tool
    draw_tool = True
    global select_tool
    select_tool = False
    global delete
    delete = False
    global is_drawing
    is_drawing = False

def fn_delete():
    global delete
    delete = True
    global select_tool
    select_tool = False
    global draw_tool
    draw_tool = False
    global is_drawing
    is_drawing = False


def _remove_suffix(file_name):
        return file_name[:-4]

def _get_first_image():
    images = os.listdir(IMG_PATH)
    if '.gitkeep' in images:
        images.remove('.gitkeep')
    image = images[0]
    return image

def _get_annotation(annotation_file):
    try:
        with open(annotation_file, 'r') as f:
            annotation = f.read()
        return annotation
    except FileNotFoundError:
         return ''

def _prune_points(points, skip_every_x_points=4):
    skip_every_x_points = skip_every_x_points*2+2
    for label in points:
        for tank_object in points[label]:
            for i in range(len(tank_object)):
                if tank_object == []:
                    continue
                if i % skip_every_x_points != 0:
                    continue
                try:
                    for j in range(skip_every_x_points-2):
                        tank_object[i+j] = None
                except IndexError:
                    pass

    # Remove the None values
    for label in points:
        for tank_object in points[label]:
            while None in tank_object:
                tank_object.remove(None)

def load_image():
    img = _get_first_image()
    cv2_im = cv2.imread(f'{IMG_PATH}/{img}')
    cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
    cv2_im = cv2.resize(cv2_im, (1280, 720))
    cv2_im = Image.fromarray(cv2_im)
    #global image
    #image = ImageTk.PhotoImage(cv2_im)
    #image_window.create_image(0, 0, anchor=tk.NW, image=image)
    return img, cv2_im

def get_annotations(img):
    annotations = _get_annotation(f'{ANNOTATION_PATH}/{_remove_suffix(img)}.txt')
    points = {}
    if annotations != '':
        for annotation in annotations.split('\n'):
            label = annotation.split(' ')[0]
            if label not in points:
                points[label] = [[]]
            else:
                points[label].append([])
            for i, val in enumerate(annotation.split(' ')[1:]):
                if i % 2 == 0:
                    v = float(val)*1280
                else:
                    v = float(val)*720
                points[label][-1].append(v)
    _prune_points(points, 4)
    return points

def draw_points_on_canvas(points):
    for label in points:
        for tank_object in points[label]:
            if tank_object == []:
                continue
            #image_window.create_polygon(tank_object, outline='red', fill='', width=2)

def show_image(event=None):
    image_window.configure(scrollregion=image_window.bbox('all'))
    bbox1 = image_window.bbox(container)
    bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
    bbox2 = (image_window.canvasx(0),
             image_window.canvasy(0),
             image_window.canvasx(image_window.winfo_width()),
             image_window.canvasy(image_window.winfo_height()))

    bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
            max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]

    if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:
        bbox[0] = bbox1[0]
        bbox[2] = bbox1[2]
    if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:
        bbox[1] = bbox1[1]
        bbox[3] = bbox1[3]

    x1 = max(bbox2[0] - bbox1[0], 0)
    y1 = max(bbox2[1] - bbox1[1], 0)
    x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
    y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
    if int(x2 - x1) > 0 and int(y2 - y1) > 0:
        x = min(int(x2 / imscale), 1280)
        y = min(int(y2 / imscale), 720)
        image = scaled_image.crop((int(x1 / imscale), int(y1 / imscale), x, y))
        
        imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
        imageid = image_window.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                           anchor='nw', image=imagetk)
        #image_window.tag_lower(imageid)
        image_window.lower(imageid)
        image_window.imagetk = imagetk


def wheel(event):
    global imscale
    global container
    
    x = image_window.canvasx(event.x)
    y = image_window.canvasy(event.y)
    bbox = image_window.bbox(container)
    if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass
    else: return
    scale = 1.0
    if event.delta == -120:
        i = min(image_window.winfo_width(), image_window.winfo_height())
        if int(i * 1) < 30: return
        imscale /= 1.1
        scale /= 1.1
    if event.delta == 120:
        i = min(image_window.winfo_width(), image_window.winfo_height())
        if i < imscale: return
        imscale *= 1.1
        scale *= 1.1

    for o in objects:
        o.scale_points(x, y, scale, scale) 
        
    image_window.scale('all', x, y, scale, scale)
    show_image()

def change_label():
    global chosen_object
    new_label = label_var.get()
    new_label_index = f"{list(label_table.values()).index(new_label)}"
    chosen_object.label = new_label_index
    chosen_object = None

is_drawing = False
def draw_new_object(event):
    if not draw_tool:
        return
    global objects
    x = image_window.canvasx(event.x)
    y = image_window.canvasy(event.y)
    global is_drawing
    if not is_drawing:
        is_drawing = True
        objects.append(TankObject('3', [x, y], first=True))
        objects[-1].points[-1].circle = image_window.create_oval(x-3, y-3, x+3, y+3, fill='blue', outline='black', width=2)
        image_window.tag_bind(objects[-1].points[-1].circle, '<Button-1>', objects[-1].points[-1].button_1_modes) # Look at this
        image_window.tag_bind(objects[-1].points[-1].circle, '<B1-Motion>', objects[-1].points[-1].drag_point)
        image_window.tag_bind(objects[-1].points[-1].circle, '<ButtonRelease-1>', objects[-1].points[-1].put_circle_on_top)
        objects[-1].points[-1].display_class()
    else:
        objects[-1].points.append(Point(x, y, objects[-1]))
        objects[-1].points[-1].left_neighbour = objects[-1].points[-1].parent.points[-2]
        objects[-1].points[-1].left_neighbour.right_neighbour = objects[-1].points[-1]
        objects[-1].points[0].left_neighbour = objects[-1].points[-1]
        objects[-1].points[-1].right_neighbour = objects[-1].points[0]

        try: 
            objects[-1].points[-1].left_neighbour._delete_line()
        except AttributeError:
            pass
        objects[-1].points[-1].left_neighbour._draw_line()
        objects[-1].points[-1]._draw_line()
        objects[-1].points[-1].circle = image_window.create_oval(x-3, y-3, x+3, y+3, fill='blue', outline='black', width=2)
        image_window.tag_bind(objects[-1].points[-1].circle, '<Button-1>', objects[-1].points[-1].button_1_modes)
        image_window.tag_bind(objects[-1].points[-1].circle, '<B1-Motion>', objects[-1].points[-1].drag_point)
        image_window.tag_bind(objects[-1].points[-1].circle, '<ButtonRelease-1>', objects[-1].points[-1].put_circle_on_top)
        objects[-1].points[-1].display_class()

def save_annotation(event=None):
    global objects
    global img
    global scaled_image
    global points
    global is_drawing

    is_drawing = False

    for o in objects:
        o.clear_points()
    with open(f'{EXPORT_PATH}/{_remove_suffix(img)}.txt', 'w') as f:
        for o in objects:
            if o.points == []:
                print("continue")
                continue
            f.write(f"{o.label} ")
            for p_i, p in enumerate(o.points):
                if p_i == len(o.points)-1:
                    f.write(f"{p.x/1280} {p.y/720}")
                    continue
                f.write(f"{p.x/1280} {p.y/720} ")
            f.write('\n')
    try:
        os.remove(f'{ANNOTATION_PATH}/{_remove_suffix(img)}.txt')
    except FileNotFoundError:
        pass
    os.rename(f'{IMG_PATH}/{img}', f'{EXPORT_PATH}/{img}')

    # Load the next image
    img = _get_first_image()
    
    points = get_annotations(img)
    objects = []
    for label in points:
        for tank_object in points[label]:
            objects.append(TankObject(label, tank_object))
    
    img, scaled_image = load_image()
    show_image()
    image_window.update()

    

# Vertical and horizontal scrollbars for canvas
vbar = AutoScrollbar(window, orient='vertical')
hbar = AutoScrollbar(window, orient='horizontal')
vbar.grid(row=0, column=2, sticky='ns')
hbar.grid(row=2, column=1, sticky='we')

select_button = tk.Button(window, text='Select Tool', command=fn_select_tool)

draw_button = tk.Button(window, text='Draw Tool', command=fn_draw_tool)

delete_button = tk.Button(window, text='Delete', command=fn_delete)

# Create the label field
label_var = tk.StringVar(window)
label_var.set(label_table['3'])
label_field = tk.OptionMenu(window, label_var, *label_table.values())

# Create the change label button
change_label_button = tk.Button(window, text='Change Label', command=change_label)

# Create the image window width=1280, height=720
image_window = tk.Canvas(window, xscrollcommand=hbar.set, yscrollcommand=vbar.set, width=1280, height=720)
container = image_window.create_rectangle(0, 0, 1280, 720, width=0)
#container = image_window.bbox(container)

img, scaled_image = load_image()
points = get_annotations(img)

objects = []
for label in points:
    for tank_object in points[label]:
        objects.append(TankObject(label, tank_object))

image_window.config(cursor='left_ptr')

# Zoom 
image_window.bind('<MouseWheel>', wheel)
image_window.bind('<Configure>', show_image)
image_window.bind('<Button-1>', draw_new_object)

# Create the save annotation button
save_annotation_button = tk.Button(window, text='Save Annotation', command=save_annotation)

# Place elements to where they should be
select_button.grid(row=1, column=0)
draw_button.grid(row=2, column=0)
delete_button.grid(row=3, column=0)
image_window.grid(row=0, column=1, sticky='nswe')
image_window.update()

def y_scroll(*args):
    image_window.yview(*args)
    show_image()
    for o in objects:
        for p in o.points:
            p

def x_scroll(*args):
    image_window.xview(*args)
    show_image()

vbar.configure(command=y_scroll)
hbar.configure(command=x_scroll)

label_field.grid(row=3, column=1)
change_label_button.grid(row=4, column=1)
save_annotation_button.grid(row=3, column=3)

# Run the window
window.mainloop()