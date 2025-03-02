from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Function to convert RGB to luminance
def get_luminance(rgb):
    def channel_lum(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

# Function to calculate contrast ratio
def get_contrast_ratio(color1, color2):
    lum1, lum2 = get_luminance(color1), get_luminance(color2)
    L1, L2 = max(lum1, lum2), min(lum1, lum2)
    return (L1 + 0.05) / (L2 + 0.05)

# Function to extract RGB values from "rgb(x, y, z)"
def parse_rgb(color):
    match = re.match(r"rgb\((\d+), (\d+), (\d+)\)", color)
    return tuple(map(int, match.groups())) if match else (255, 255, 255)  # Default to white


def analyse_website(url):


    PATH = "C:\\Program Files (x86)\\chromedriver.exe"
    # driver = webdriver.Chrome(PATH)

    options = Options()  # Create a ChromeOptions object
    service = Service(PATH)  # Use Service object

    driver = webdriver.Chrome(service=service, options=options)
    # driver.get("https://www.google.com")

    final_results = {
        "keyboard_inaccessible": [],
        "missing_alt": [],
        "missing_placeholders": [],
        "contrast_ratio_violations": [],
        "aria_violations": [],
        "invalid_roles": [],
        "content_analysis": "",
        "heading_structure": [],
        "tracking_scripts": [],
        "some_remakrs": []
    }


    try:
        #driver.get("https://www.geeksforgeeks.org/")
        driver.get(url)
        print(driver.title)
        # # searchbox = driver.find_element_by_name("gLFyf")
        # # searchbox = driver.find_element(By.CLASS_NAME, "gLFyf")
        # print(driver.page_source)
        # # searchbox.send_keys("Python")
        # # searchbox.send_keys(Keys.RETURN)
        # link = driver.find_element(By.XPATH, "//a[text()='about']")
        # link.click()

        
        expected_elements = driver.find_elements(By.CSS_SELECTOR, 
        "a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
        )

        visible_expected_elements = [elem for elem in expected_elements if elem.is_displayed()]
        expected_elements = visible_expected_elements

        expected_count = len(expected_elements)
        print(f"Expected focusable elements: {expected_count}")
        # print(expected_elements)

        # Step 2: Get actual focusable elements by tabbing
        actual_focusable = set()  # To track unique focusable elements
        start_element = driver.switch_to.active_element  # Initial focus

        while True:
            actual_focusable.add(driver.switch_to.active_element)  # Track focused elements
            driver.switch_to.active_element.send_keys(Keys.TAB)
            time.sleep(0.2)  # Small delay for UI response

            if driver.switch_to.active_element in actual_focusable:
                break  # Stop if we loop back

        actual_count = len(actual_focusable) - 6 # -6 to exclude browser UI elements
        print(f"Actual focusable elements: {actual_count}")

        # Accessibility Check
        if actual_count < expected_count:
            print("⚠️ Some elements are missing from tab order! Accessibility issue detected.")
            print(f"Expected: {expected_count}, Actual: {actual_count}")
            print('diff:', expected_count - actual_count)
            final_results["keyboard_inaccessible"] = [elem.get_attribute("outerHTML") for elem in expected_elements if elem not in actual_focusable]
        else:
            print("✅ All elements are properly focusable.")
            final_results["keyboard_inaccessible"] = []

        # Find elements that should have alt text
        alt_elements = driver.find_elements(By.TAG_NAME, "img")

        # Filter only visible elements
        visible_alt_elements = [elem for elem in alt_elements if elem.is_displayed()]

        # Check if they have a valid alt attribute
        missing_alt = []
        valid_alt = []

        for elem in visible_alt_elements:
            alt_text = elem.get_attribute("alt")

            if not alt_text or alt_text.strip() == "":
                missing_alt.append(elem.get_attribute("outerHTML"))  # Store elements missing alt
            else:
                valid_alt.append((elem.tag_name, alt_text))

        # Print results
        print(f"Total visible elements needing 'alt': {len(visible_alt_elements)}")
        print(f"Elements missing 'alt': {len(missing_alt)}")
        print("----- Missing ALT Elements -----")
        for element in missing_alt:
            final_results["missing_alt"].append(element)
            final_results["some_remakrs"].append(f'{len(missing_alt)} elements missing alt text while {len(valid_alt)} elements have valid alt text')
            print(element)

        print("----- Valid ALT Elements -----")
        for tag, alt_text in valid_alt:
            print(f"{tag}: {alt_text}")



        ########## Contrast Ratio ##########
        # Find all elements with text
        elements = driver.find_elements(By.XPATH, "//*[text()]")
        violationCount = 0
        # Check contrast for each element
        for elem in elements:
            try:
                text_color = parse_rgb(driver.execute_script("return window.getComputedStyle(arguments[0]).color;", elem))
                bg_color = parse_rgb(driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor;", elem))
                
                contrast_ratio = get_contrast_ratio(text_color, bg_color)
                
                # WCAG minimum contrast thresholds
                if contrast_ratio < 4.5:
                    violationCount += 1
                    print(f"⚠️ Low contrast ({contrast_ratio:.2f}) for text: '{elem.text}'")

            
            except Exception:
                continue
            
        final_results["contrast_ratio_violations"].append(f"total {violationCount} elements with low contrast")
        
        # ✅ Check for inputs missing placeholders
        inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea")
        visible_elements = [elem for elem in inputs if elem.is_displayed()]
        inputs = visible_elements
        missing_placeholders = [
            elem for elem in inputs if not elem.get_attribute("placeholder")
        ]
        print("missing_placeholders\n")
        for elem in missing_placeholders:
            final_results["missing_placeholders"].append(f"  🔹 ID: {elem.get_attribute('id')}, Name: {elem.get_attribute('name')}, HTML: {elem.get_attribute('outerHTML')}")
            print(f"  🔹 ID: {elem.get_attribute('id')}, Name: {elem.get_attribute('name')}, HTML: {elem.get_attribute('outerHTML')}")
        

        # ✅ Check for inputs missing labels
        inputs_missing_labels = []
        for input_elem in inputs:
            id_attr = input_elem.get_attribute("id")
            label = driver.find_elements(By.CSS_SELECTOR, f"label[for='{id_attr}']")
            if not label and not input_elem.get_attribute("aria-label"):
                inputs_missing_labels.append(input_elem)

        # ✅ Check for elements missing ARIA roles
        interactive_elements = driver.find_elements(By.CSS_SELECTOR, "button, a, [onclick], [tabindex]:not([tabindex='-1'])")
        visible_elements = [elem for elem in interactive_elements if elem.is_displayed()]
        interactive_elements = visible_elements

        missing_roles = [
            elem for elem in interactive_elements
            if not elem.get_attribute("role")
        ]

        # ✅ Check for elements with incorrect ARIA attributes
        invalid_aria = []
        for elem in driver.find_elements(By.CSS_SELECTOR, "[aria-hidden], [aria-label], [aria-labelledby]"):
            if elem.get_attribute("aria-hidden") == "false" and elem.is_displayed():
                invalid_aria.append(elem)

        # ✅ Ignore elements with `display: none`
        visible_elements = [elem for elem in driver.find_elements(By.XPATH, "//*") if elem.is_displayed()]

        # 🔹 Report Findings 🔹
        print("🚨 Accessibility Violations Found 🚨")

        if missing_placeholders:
            final_results["some_remakrs"].append(f"{len(missing_placeholders)} inputs missing placeholders")
            print(f"❌ {len(missing_placeholders)} inputs missing placeholders")

        if inputs_missing_labels:
            final_results["some_remakrs"].append(f"{len(inputs_missing_labels)} inputs missing labels")
            print(f"❌ {len(inputs_missing_labels)} inputs missing labels")

        if missing_roles:
            final_results["some_remakrs"].append(f"{len(missing_roles)} interactive elements missing ARIA roles")
            print(f"❌ {len(missing_roles)} interactive elements missing ARIA roles")

        if invalid_aria:
            final_results["some_remakrs"].append(f"{len(invalid_aria)} elements have invalid ARIA attributes")
            print(f"❌ {len(invalid_aria)} elements have invalid ARIA attributes")

        if not (missing_placeholders or inputs_missing_labels or missing_roles or invalid_aria):
            print("✅ No major accessibility issues found! 🎉")



        ###############################################################################################3

        # 1️⃣ Extract Main Content
        content_elements = driver.find_elements(By.CSS_SELECTOR, 
            "p, li, article, section, div[role='main'], div[role='article']"
        )

        main_content = []
        for elem in content_elements:
            if elem.is_displayed():  # Ignore hidden elements
                main_content.append(elem.text.strip())

        # 2️⃣ Extract Headings & Validate Structure
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        heading_structure = []

        for heading in headings:
            if heading.is_displayed():
                tag = heading.tag_name
                text = heading.text.strip()
                heading_structure.append((tag, text))

        # 3️⃣ Analyze Heading Hierarchy Issues
        missing_h1 = not any(h[0] == "h1" for h in heading_structure)
        final_results["heading_structure"] = heading_structure
        incorrect_hierarchy = []

        prev_level = 0
        for tag, text in heading_structure:
            level = int(tag[1])  # Extract heading level (h1 -> 1, h2 -> 2, etc.)
            if level > prev_level + 1:
                incorrect_hierarchy.append((tag, text))
            prev_level = level

        # 📌 Print Results
        print("\n🔹 Extracted Main Content for LLM Analysis:\n")
        print("\n".join(main_content))

        print("\n🔹 Heading Structure Analysis:\n")
        for tag, text in heading_structure:
            print(f"  {tag.upper()}: {text}")

        if missing_h1:
            final_results["some_remakrs"].append("Missing <h1> on the page")
            print("\n❌ Missing <h1> on the page!")

        if incorrect_hierarchy:
            print("\n⚠️ Incorrect Heading Hierarchy:")
            for tag, text in incorrect_hierarchy:
                print(f"  ⏳ {tag.upper()} used incorrectly before: {text}")

        # ✅ Send `main_content` to LLM for readability scoring (API or manual review

        ####################################################################################################
        # 1️⃣ Check for Privacy Policy Link
        privacy_links = driver.find_elements(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'privacy')]")

        if privacy_links:
            print("✅ Privacy Policy Found!")
            final_results["some_remakrs"].append(f"Privacy Policy Found: {len(privacy_links)} links")
            for link in privacy_links:
                print(f"🔗 {link.get_attribute('href')}")
        else:
            final_results["some_remakrs"].append("Privacy Policy Missing!")
            print("❌ Privacy Policy Missing!")

        # 2️⃣ Check for Cookie Consent Banner
        cookie_banner = driver.find_elements(By.XPATH, "//*[contains(text(), 'cookie') or contains(text(), 'Cookie')]")

        if cookie_banner:
            final_results["some_remakrs"].append("Cookie Banner Detected")
            print("✅ Cookie Banner Detected")
        else:
            final_results["some_remakrs"].append("No Cookie Consent Banner Found!")
            print("❌ No Cookie Consent Banner Found!")

        # 3️⃣ Analyze Cookie Options (Opt-in vs. Opt-out)
        accept_button = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]")
        reject_button = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reject')]")

        if accept_button and reject_button:
            print("✅ Cookie Banner Provides Accept & Reject Options (Compliant)")
        elif accept_button and not reject_button:
            print("⚠️ Only Accept Button Found (Might Not Be GDPR-Compliant)")
        else:
            print("❌ No Clear Cookie Control Options!")

        # 4️⃣ Find Tracking Scripts & Third-Party Cookies
        tracking_scripts = driver.execute_script("""
        return [...document.querySelectorAll("script[src]")].map(s => s.src).filter(url => url.includes('analytics') || url.includes('track') || url.includes('facebook') || url.includes('google'))
        """)

        if tracking_scripts:
            print("\n🔍 Found Tracking Scripts:")
            final_results["some_remakrs"].append(f"Found {len(tracking_scripts)} tracking scripts")
            for script in tracking_scripts:
                final_results["tracking_scripts"].append(script)
                print(f"  - {script}")
        else:
            print("✅ No Tracking Scripts Detected!")
            final_results["some_remakrs"].append("No tracking scripts detected")




        ###############################################################################################
        # 1️⃣ Look for Contact & Feedback Links
        contact_links = driver.find_elements(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact') or contains(text(), 'feedback')]")

        if contact_links:
            print("✅ Contact/Feedback Link Found!")
            final_results["some_remakrs"].append(f"Found {len(contact_links)} contact/feedback links")
            for link in contact_links:
                print(f"🔗 {link.get_attribute('href')}")
        else:
            print("❌ No Contact/Feedback Link Found!")
            final_results["some_remakrs"].append("No contact/feedback links found")

        ############################################################################################
        # 1️⃣ Find Skip Links (Anchor tags pointing to IDs like #main)
        skip_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, '#')]")

        valid_skip_links = []
        for link in skip_links:
            target_id = link.get_attribute("href").split("#")[-1]
            if driver.find_elements(By.ID, target_id):  # Check if target exists
                valid_skip_links.append(link)

        # 2️⃣ Print Results
        if valid_skip_links:
            print(f"✅ {len(valid_skip_links)} Skip Links Found!")
            final_results["some_remakrs"].append(f"Found {len(valid_skip_links)} valid skip links")
            for link in valid_skip_links:
                print(f"🔗 {link.get_attribute('href')}")
        else:
            print("❌ No Valid Skip Links Found!")
            final_results["some_remakrs"].append("No valid skip links found")

        print("final_results")
        print(final_results)
        llm_ip = f"""
        🚀 **Accessibility Audit Report** 🚀

        🎹 **Keyboard Accessibility Issues**
        - {len(final_results['keyboard_inaccessible'])} elements are not accessible via keyboard.
        - Affected elements: {final_results['keyboard_inaccessible']}

        🖼️ **Image Accessibility (ALT Text)**
        - {len(final_results['missing_alt'])} images are missing ALT text.
        - Images found: {final_results['missing_alt']}

        🔡 **Form Accessibility**
        - {len(final_results['missing_placeholders'])} input fields are missing placeholders.
        - Fields affected: {final_results['missing_placeholders']}

        🌗 **Contrast Ratio Violations**
        - {len(final_results['contrast_ratio_violations'])} elements have insufficient contrast.
        - Affected elements: {final_results['contrast_ratio_violations']}

        🎭 **ARIA Violations**
        - {len(final_results['aria_violations'])} elements have ARIA-related issues.
        - Issues found: {final_results['aria_violations']}

        ⚠️ **Invalid Roles**
        - {len(final_results['invalid_roles'])} elements have incorrect or missing roles.
        - Elements affected: {final_results['invalid_roles']}

        📑 **Content Readability & Structure**
        - Readability Score: {final_results['content_analysis']}
        - Heading Structure Analysis: {final_results['heading_structure']}

        💡 **Other Important Findings**
        {final_results['some_remakrs']}
        """

        print(llm_ip)
        return llm_ip

        # ✅ Close WebDriver
        driver.quit()
        
        input("Press Enter to exit...")  # Keeps browser open
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()



