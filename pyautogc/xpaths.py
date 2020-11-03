"""
All the xpath selectors used in this modules. For the sake of organization,
xpaths here are grouped by the google classroom view they are used in, and there
is one class for housing the xpaths relevant to each view. However, they are
merged at the bottom of the file into a single entrypoint; the "Xpaths" class
which inherits all the classes in this file. Obviously, it will be important
to avoid naming conflicts as more xpaths are added.

Some target a single specific element, while others grab lists of elements with
wildcard selectors at some position within them. I've tried to document each
xpath, especially the ones that do non-trivial or unobvious things, for ease
of updating in case of a frontend update to Google Classroom.
"""


class Login:
    # username text input
    login_username = '//*[@id="identifierId"]'
    # password text input
    login_password = (
        '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/'
        'div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/'
        'div/div[1]/input'
    )


class Homepage:
    # select all anchor tags which contain hrefs to each classroom
    homepage_anchor_tags_for_each_classroom = (
        '/html/body/div[2]/div/div[2]/div/ol/li/div[1]/div[3]/h2/a[1]'
    )


class Classwork:
    """
    All prefixed with cw_
    """
    # select all the spans in the classwork view that contain assignment names.
    # used in the process of finding links to assignment view of a particular
    # assignment by name
    cw_all_assignment_names = (
        '/html/body/div[2]/div/main/div/div/div[4]/ol/li/div/div/div/div/ol/li'
        '/div/div/div/div/div/span'
    )
    # After the span with the correct assignment name is found, this xpath
    # is used to traverse up the tree, then back down to the anchor tag
    # containaing the necessary href
    cw_anchor_tag_relative_to_assignment_name_span = (
        './../../../../../div[2]/div[2]/div/a'
    )


class Feedback:
    """
    All prefixed with fb_
    """
    # text input element in the menu bar that allows you to pull up specific
    # menu items, thereby interacting with dropdown menus
    fb_menu_bar_text_search = (
        '/html/body/div[1]/div[4]/div[2]/div[1]/div[1]/div/input'
    )

    fb_next_student_button = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[2]/div[2]'
    )

    # text input field for private comment to student
    fb_private_comment_input = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div/'
        'div[3]/div/div[1]/c-wiz/div/div[2]/div[1]/div[1]/div[2]/textarea'
    )

    # button to post private comment to student
    fb_private_comment_submit = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/'
        'div/div[3]/div/div[1]/c-wiz/div/div[2]/div[2]/div[2]'
    )

    # text input field for student grade
    fb_grade_input = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/'
        'div/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[1]/input'
    )

    # drawer that holds google slide thumbnails, nested within an iframe
    fb_google_slide_thumbnail_drawer = (
        '/html/body/div[4]/div/table/tbody/tr/td[1]/div[2]/div'
    )

    # open dropdown of all students
    fb_student_dropdown_xpath = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div'
    )

    # button that sorts students by status in the aformentioned dropdown
    fb_status_sort_button_xpath = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[2]'
        '/div[1]/div[4]/div[3]/span[3]'
    )

    # xpath to the first student in the dropdown after sorting, who will need
    # to be clicked on after sorting to ensure that we are at the start of the
    # list
    fb_first_student_in_dropdown = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[2]'
        '/div[2]/div[1]'
    )

    # grade divisor
    fb_grade_divisor = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/'
        'div[1]/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/span/span'
        '/span'
    )

    # wacky values in the dropdown when it's closed. See docstring for
    # FeedbackUtils._av_get_current_name() for details
    fb_dropdown_values = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[1]'
        '/div[1]/div[*]/span/div/div[1]'
    )

    # regardless of whether there are one or two attachments, this is the
    # parent element. This is useful, because we can wait for this element to
    # mount before checking for children.
    fb_attachments_common_parent = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
        '/div[1]/div[2]/div/div[2]/div/div/div'
    )

    # label if there is a single attachment
    fb_single_attachment_label = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
        '/div[1]/div[2]/div/div[2]/div/div/div/span/div[2]/div/span[2]'
    )

    # all labels if there are more than one attachments
    fb_multiple_attachment_label = (
        '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/div[1]/div'
        '/div[1]/div[2]/div/div[2]/div/div/div/div/span/div/div/span[2]'
    )

    @staticmethod
    def fb_attachment_label_xpath(index):
        """
        This element can ultimately be clicked on to switch to the attachment
        it is for. It must be dynamically assigned by index.
        """
        xpath = (
            '/html/body/div[4]/c-wiz/c-wiz/main/div[2]/div[2]/div[2]/di'
            f'v[1]/div/div[1]/div[2]/div/div[2]/div/div[{index}]/div/div/sp'
            f'an/div[{index}]/div/span[2]'
        )
        return xpath


class Xpaths(Classwork, Login, Homepage, Feedback):
    pass
