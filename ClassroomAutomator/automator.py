import os
from time import sleep
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import pyautogui as pg


class ClassroomAutomator:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Firefox()
        self.driver.get('https://classroom.google.com/u/1/h')
        xpath = '//*[@id="identifierId"]'
        username_elem = self.driver.find_element_by_xpath(xpath)
        username_elem.clear()
        username_elem.send_keys(self.username)
        username_elem.send_keys(Keys.RETURN)
        sleep(2.1)
        xpath = (
            '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/'
            'div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]'
            '/div/div/div/div/div[1]/div/div[1]/input'
        )
        password_elem = self.driver.find_element_by_xpath(xpath)
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        sleep(1)

    def clickthrough_doc(self, scroll_down):
        """
        scroll_down is an integer that determines how for down the doc it will
        scroll to show only critical information.

        Returns student name and assignment status. NOTE: This will always leave
        the cursor in the comment box, so other pyautogui things can be done
        afterwards.
        """
        pg.PAUSE = 1
        pg.click(x=542, y=432)  # onto next student
        pg.click(x=596, y=161)  # onto next student
        sleep(0.5)

        if scroll_down:
            pg.moveTo(x=1120, y=264)
            pg.dragTo(x=1120, y=(scroll_down + 264), button='left')

        # make comment
        pg.click(x=1285, y=406)

        try:
            # identify name and assignment status of currently selected student
            name_divs = self.driver.find_elements(
                'xpath',
                '/html/body/div[4]/c-wiz/c-wiz/main/div[1]/div[1]/div[1]/div/div[1]/div[1]/*',
            )
            names_and_statuses = (
                [d.text.split('\n') for d in name_divs if d.get_attribute('aria-checked') == 'true']
            )
            if len(names_and_statuses[0]) == 2:
                name, assignment_status = names_and_statuses[0]
            elif len(names_and_statuses[0]) == 3:
                name, _, assignment_status = names_and_statuses[0]  # ['name', 'turned in', 'done late']
            else:
                raise Exception(
                    'Incorrect pre-concieved-notion error: detected more than one '
                    'currently selected student.'
                )
                breakpoint()

        except Exception as e:
            print(f'exception {e}')
            breakpoint()

        return name, assignment_status

    def get_assignment_link(self, homeroom_url, assignment_name):
        """
        Take assignment name as a string and return the link to that assignment,
        with the presumption that the driver is navigated to the stream of
        a google classroom.
        """


        self.driver.get(homeroom_url)
        sleep(3)

        # another day
        """
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, f'Assignment: {assignment_name}'))
            )
        finally:
            print('classroom loading took more than ten seconds')
            self.driver.close()
        """


        while True:
            try:
                anchor_tags = self.driver.find_elements('tag name', 'a')
                anchor_tag = [a for a in anchor_tags if a.get_attribute('aria-label') == f'Assignment: "{assignment_name}"'][0]
                break
            except StaleElementReferenceException:
                print('finding title element taking longer than expected')
                sleep(1)
            except IndexError:
                print('finding title element taking longer than expected')
                sleep(1)
            except Exception as e:
                print(f'unexpected exception: {e}')
                sleep(1)
        if not anchor_tag:
            pg.hotkey('command', 'tab')
            for tag in anchor_tags:
                try:
                    arr = tag.get_attribute('aria-label').split('"')
                except AttributeError:
                    print('Attribute error on tag')
                    return None
                    continue
                if 'Assignment' in arr[0]:
                    inp = input(
                        f'Could not find an exact match for the assignment '
                        f'"{assignment_name}." Did you mean {arr[1]}? (y/n)'
                    )
                    if inp == 'y':
                        anchor_tag = [a for a in anchor_tags if a.get_attribute('aria-label') == f'Assignment: "{arr[1]}"'][0]
                        break

        if not anchor_tag:
            # user or program did not identify a match
            print('exiting because link was not found')
            self.driver.close()
            sys.exit()
        
        root_href = anchor_tag.get_attribute('href')
        ext = root_href.split('/')
        processed_href = f'https://classroom.google.com/g/tg/{ext[4]}/{ext[6]}'
        return processed_href
