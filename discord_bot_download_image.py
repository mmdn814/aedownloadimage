import discord
import os
import requests
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



async def download_images(product_id, product_url):
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    # Define the download function
    def download_file(file_url, folder_path, filename):
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(os.path.join(folder_path, filename), 'wb') as file:
                file.write(response.content)

    # Open the product page
    driver.get(product_url)
    driver.implicitly_wait(10)  # Adjust the time as needed

    # Wait for the slider to load
    slider = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.slider--box--TJYmEtw')))

    # Find all the div elements inside the slider and hover over them
    div_elements = driver.find_elements(By.CSS_SELECTOR, '.slider--box--TJYmEtw div')

    # Create a folder to save the downloaded images and videos
    folder_path = os.path.join(os.getcwd(), str(product_id))
    os.makedirs(folder_path, exist_ok=True)

    # Loop through each div element
    for i, div in enumerate(div_elements):
        # Hover over the div element
        actions = ActionChains(driver)
        actions.move_to_element(div).perform()

        # Parse the HTML code of the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        elements = soup.select('.image-view--previewBox--FyWaIlU  *')  # Selects all children of the class

        # Loop through each element
        for j, element in enumerate(elements):
            if element.name == 'img':
                img_url = element['src'] if element['src'].startswith('http') else 'https:' + element['src']
                download_file(img_url, folder_path, f'image_{i}_{j}.jpg')
            elif element.name == 'video':
                video_sources = element.find_all('source')
                if video_sources:
                    video_url = video_sources[0]['src']
                    download_file(video_url, folder_path, f'video_{i}_{j}.mp4')
            if j >= len(elements) - 1:  # Break the loop when all images and videos have been downloaded
                break

        # Check if there is a next page
        next_page = driver.find_elements(By.CSS_SELECTOR, '.slider--next--_kdczx2')
        if not next_page:
            break

        # Click the next page button
        next_page[0].click()

        # Wait for the slider to load
        slider = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.slider--box--TJYmEtw')))

        # Find all the div elements inside the slider and hover over them
        div_elements = driver.find_elements(By.CSS_SELECTOR, '.slider--box--TJYmEtw div')

    # Close the WebDriver
    driver.close()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    # Check if the message starts with "!download"
    if message.content.startswith('!download'):
        # Split the message into parts
        parts = message.content.split(' ')
        # Get the product ID and URL from the message
        product_id = parts[1]
        product_url = parts[2]
        # Call the download_images function to download the images and videos
        await download_images(product_id, product_url)
        # Send a message to the Discord channel to confirm that the images have been downloaded
        await message.channel.send(f'Downloaded images and videos for product ID {product_id} from {product_url}')

client.run('MTIyNjczNzQyMzU3MzE4ODY1OQ.GCQJrU.MeUIP4ji85jlUJRBmAJ_FfU7gCQh1a61D-m2Vc')
