/**
 * Button Click Tracker for Puppeteer
 * Tracks button clicks and logs detailed information for creating page locators
 */

/**
 * Sets up comprehensive button click tracking on a Puppeteer page
 * @param {import('puppeteer').Page} page - The Puppeteer page instance
 * @param {Object} options - Configuration options
 * @param {boolean} options.enableConsoleLog - Whether to log to console (default: true)
 * @param {boolean} options.enableFileLog - Whether to save logs to file (default: false)
 * @param {string} options.logFilePath - Path for log file (default: './button-clicks.log')
 * @param {boolean} options.trackAllElements - Whether to track all clickable elements, not just buttons (default: false)
 * @param {boolean} options.captureScreenshot - Whether to capture screenshots on clicks (default: false)
 * @param {string} options.screenshotDir - Directory for screenshots (default: './click-screenshots')
 * @returns {Promise<void>}
 */
export async function setupButtonClickTracker(page, options = {}) {
    const {
        enableConsoleLog = true,
        enableFileLog = false,
        logFilePath = './button-clicks.log',
        trackAllElements = false,
        captureScreenshot = false,
        screenshotDir = './click-screenshots'
    } = options;

    let clickCounter = 0;
    const fs = enableFileLog ? await import('fs/promises') : null;

    // Create screenshot directory if needed
    console.log('creating screenshot directory')
    if (captureScreenshot && fs) {
        try {
            await fs.mkdir(screenshotDir, { recursive: true });
        } catch (error) {
            console.warn('Could not create screenshot directory:', error.message);
        }
    }

    /**
     * Logs click information
     * @param {Object} clickData - Data about the clicked element
     */
    console.log('defining log click')
    async function logClick(clickData) {
        console.log('logging click')
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            clickNumber: ++clickCounter,
            ...clickData
        };

        const logString = JSON.stringify(logEntry, null, 2);

        if (enableConsoleLog) {
            console.log('\n=== BUTTON CLICK TRACKED ===');
            console.log(logString);
            console.log('=== END TRACKING ===\n');
        }

        if (enableFileLog && fs) {
            console.log('writing to log file')
            try {
                await fs.appendFile(logFilePath, logString + '\n\n');
            } catch (error) {
                console.error('Failed to write to log file:', error.message);
            }
        }
    }

    /**
     * Captures screenshot of the clicked element
     * @param {import('puppeteer').ElementHandle} element - The clicked element
     * @param {number} clickNumber - The click counter
     */
    async function captureElementScreenshot(element, clickNumber) {
        if (!captureScreenshot) return;

        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `${screenshotDir}/click-${clickNumber}-${timestamp}.png`;
            await element.screenshot({ path: filename });
            console.log(`Screenshot saved: ${filename}`);
        } catch (error) {
            console.warn('Failed to capture screenshot:', error.message);
        }
    }

    /**
     * Extracts comprehensive element information for locator creation
     * @param {import('puppeteer').ElementHandle} element - The element to analyze
     * @returns {Promise<Object>} Element information
     */
    async function extractElementInfo(element) {
        console.log('extracting element info')
        try {
            const elementInfo = await element.evaluate((el) => {
                const rect = el.getBoundingClientRect();
                const computedStyle = window.getComputedStyle(el);
                
                // Get all attributes
                const attributes = {};
                for (let attr of el.attributes) {
                    attributes[attr.name] = attr.value;
                }

                // Get text content (cleaned)
                const textContent = el.textContent?.trim() || '';
                const innerText = el.innerText?.trim() || '';

                // Get parent information
                const parent = el.parentElement;
                const parentInfo = parent ? {
                    tagName: parent.tagName,
                    className: parent.className,
                    id: parent.id,
                    attributes: Object.fromEntries(
                        Array.from(parent.attributes).map(attr => [attr.name, attr.value])
                    )
                } : null;

                // Get sibling information
                const siblings = Array.from(el.parentElement?.children || [])
                    .filter(child => child !== el)
                    .slice(0, 3) // Limit to first 3 siblings
                    .map(sibling => ({
                        tagName: sibling.tagName,
                        className: sibling.className,
                        textContent: sibling.textContent?.trim().substring(0, 50)
                    }));

                return {
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id,
                    attributes,
                    textContent,
                    innerText,
                    ariaLabel: el.getAttribute('aria-label'),
                    title: el.getAttribute('title'),
                    role: el.getAttribute('role'),
                    type: el.getAttribute('type'),
                    name: el.getAttribute('name'),
                    value: el.getAttribute('value'),
                    href: el.getAttribute('href'),
                    src: el.getAttribute('src'),
                    alt: el.getAttribute('alt'),
                    dataAttributes: Object.fromEntries(
                        Array.from(el.attributes)
                            .filter(attr => attr.name.startsWith('data-'))
                            .map(attr => [attr.name, attr.value])
                    ),
                    position: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    styles: {
                        backgroundColor: computedStyle.backgroundColor,
                        color: computedStyle.color,
                        fontSize: computedStyle.fontSize,
                        fontWeight: computedStyle.fontWeight,
                        display: computedStyle.display,
                        visibility: computedStyle.visibility,
                        opacity: computedStyle.opacity
                    },
                    parent: parentInfo,
                    siblings,
                    isVisible: rect.width > 0 && rect.height > 0 && 
                               computedStyle.visibility !== 'hidden' && 
                               computedStyle.display !== 'none',
                    isClickable: computedStyle.pointerEvents !== 'none' && 
                                computedStyle.cursor === 'pointer'
                };
            });

            return elementInfo;
        } catch (error) {
            console.warn('Failed to extract element info:', error.message);
            return { error: error.message };
        }
    }

    /**
     * Generates locator suggestions based on element information
     * @param {Object} elementInfo - Element information
     * @returns {Array<string>} Array of locator suggestions
     */
    function generateLocatorSuggestions(elementInfo) {
        console.log('generating locator suggestions')
        const suggestions = [];

        // ID-based locator (most specific)
        if (elementInfo.id) {
            suggestions.push(`#${elementInfo.id}`);
        }

        // Class-based locators
        if (elementInfo.className) {
            const classes = elementInfo.className.split(' ').filter(c => c.trim());
            classes.forEach(cls => {
                if (cls) suggestions.push(`.${cls}`);
            });
        }

        // Tag + class combinations
        if (elementInfo.className) {
            const classes = elementInfo.className.split(' ').filter(c => c.trim());
            classes.forEach(cls => {
                if (cls) suggestions.push(`${elementInfo.tagName.toLowerCase()}.${cls}`);
            });
        }

        // Text-based locators
        if (elementInfo.textContent) {
            suggestions.push(`text="${elementInfo.textContent}"`);
        }

        if (elementInfo.innerText) {
            suggestions.push(`text="${elementInfo.innerText}"`);
        }

        // Attribute-based locators
        if (elementInfo.ariaLabel) {
            suggestions.push(`[aria-label="${elementInfo.ariaLabel}"]`);
        }

        if (elementInfo.title) {
            suggestions.push(`[title="${elementInfo.title}"]`);
        }

        if (elementInfo.role) {
            suggestions.push(`[role="${elementInfo.role}"]`);
        }

        if (elementInfo.type) {
            suggestions.push(`[type="${elementInfo.type}"]`);
        }

        if (elementInfo.name) {
            suggestions.push(`[name="${elementInfo.name}"]`);
        }

        if (elementInfo.href) {
            suggestions.push(`[href="${elementInfo.href}"]`);
        }

        // Data attribute locators
        Object.entries(elementInfo.dataAttributes || {}).forEach(([key, value]) => {
            suggestions.push(`[${key}="${value}"]`);
        });

        // XPath suggestions
        if (elementInfo.id) {
            suggestions.push(`xpath=//*[@id="${elementInfo.id}"]`);
        }

        if (elementInfo.textContent) {
            suggestions.push(`xpath=//${elementInfo.tagName.toLowerCase()}[text()="${elementInfo.textContent}"]`);
        }

        // Position-based (for debugging)
        suggestions.push(`xpath=//${elementInfo.tagName.toLowerCase()}[position()=1]`);

        return suggestions.filter((s, i, arr) => arr.indexOf(s) === i); // Remove duplicates
    }

    // Set up click event listener
    await page.evaluateOnNewDocument((trackAllElements) => {
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        const originalClick = HTMLElement.prototype.click;

        // Track programmatic clicks
        HTMLElement.prototype.click = function(...args) {
            const element = this;
            setTimeout(() => {
                window.dispatchEvent(new CustomEvent('puppeteerClickTracked', {
                    detail: { element, method: 'programmatic' }
                }));
            }, 0);
            return originalClick.apply(this, args);
        };

        // Track event listener clicks
        EventTarget.prototype.addEventListener = function(type, listener, ...args) {
            if (type === 'click') {
                const wrappedListener = function(event) {
                    const element = event.target;
                    if (trackAllElements || element.tagName === 'BUTTON' || 
                        element.tagName === 'A' || element.tagName === 'INPUT' ||
                        element.role === 'button' || element.onclick) {
                        window.dispatchEvent(new CustomEvent('puppeteerClickTracked', {
                            detail: { element, method: 'eventListener', event }
                        }));
                    }
                    return listener.apply(this, arguments);
                };
                return originalAddEventListener.call(this, type, wrappedListener, ...args);
            }
            return originalAddEventListener.call(this, type, listener, ...args);
        };

        // Also track direct onclick assignments
        Object.defineProperty(HTMLElement.prototype, 'onclick', {
            set: function(value) {
                this._onclick = value;
                if (value) {
                    this.addEventListener('click', value);
                }
            },
            get: function() {
                return this._onclick;
            }
        });

    }, trackAllElements);

    // Listen for click events
    await page.exposeFunction('logClickToNode', async (elementInfo) => {
        const locatorSuggestions = generateLocatorSuggestions(elementInfo);
        
        const clickData = {
            url: page.url(),
            elementInfo,
            locatorSuggestions,
            recommendedLocator: locatorSuggestions[0] || 'No specific locator found'
        };

        await logClick(clickData);
    });

    // Set up the event listener in the page context
    await page.evaluate(() => {
        console.log('setting up event listener')
        window.addEventListener('puppeteerClickTracked', async (event) => {
            const { element } = event.detail;
            
            // Extract element information
            const elementInfo = await window.extractElementInfo(element);
            
            // Log to Node.js
            await window.logClickToNode(elementInfo);
        });

        // Expose element info extraction function
        window.extractElementInfo = async (element) => {
            const rect = element.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(element);
            
            const attributes = {};
            for (let attr of element.attributes) {
                attributes[attr.name] = attr.value;
            }

            return {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                attributes,
                textContent: element.textContent?.trim() || '',
                innerText: element.innerText?.trim() || '',
                ariaLabel: element.getAttribute('aria-label'),
                title: element.getAttribute('title'),
                role: element.getAttribute('role'),
                type: element.getAttribute('type'),
                name: element.getAttribute('name'),
                value: element.getAttribute('value'),
                href: element.getAttribute('href'),
                src: element.getAttribute('src'),
                alt: element.getAttribute('alt'),
                dataAttributes: Object.fromEntries(
                    Array.from(element.attributes)
                        .filter(attr => attr.name.startsWith('data-'))
                        .map(attr => [attr.name, attr.value])
                ),
                position: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                },
                styles: {
                    backgroundColor: computedStyle.backgroundColor,
                    color: computedStyle.color,
                    fontSize: computedStyle.fontSize,
                    fontWeight: computedStyle.fontWeight,
                    display: computedStyle.display,
                    visibility: computedStyle.visibility,
                    opacity: computedStyle.opacity
                },
                isVisible: rect.width > 0 && rect.height > 0 && 
                           computedStyle.visibility !== 'hidden' && 
                           computedStyle.display !== 'none',
                isClickable: computedStyle.pointerEvents !== 'none' && 
                            computedStyle.cursor === 'pointer'
            };
        };
    });

    console.log('✅ Button click tracker initialized successfully!');
    console.log(`📊 Tracking ${trackAllElements ? 'all clickable elements' : 'buttons only'}`);
    if (enableFileLog) {
        console.log(`📝 Logs will be saved to: ${logFilePath}`);
    }
    if (captureScreenshot) {
        console.log(`📸 Screenshots will be saved to: ${screenshotDir}`);
    }
}

/**
 * Gets click statistics from the tracking session
 * @param {import('puppeteer').Page} page - The Puppeteer page instance
 * @returns {Promise<Object>} Click statistics
 */
export async function getClickStatistics(page) {
    return await page.evaluate(() => {
        return {
            totalClicks: window.clickCounter || 0,
            trackedElements: window.trackedElements || []
        };
    });
}

/**
 * Stops the click tracking
 * @param {import('puppeteer').Page} page - The Puppeteer page instance
 */
export async function stopButtonClickTracker(page) {
    await page.evaluate(() => {
        // Remove event listeners
        window.removeEventListener('puppeteerClickTracked', window.puppeteerClickHandler);
        
        // Restore original methods
        if (window.originalAddEventListener) {
            EventTarget.prototype.addEventListener = window.originalAddEventListener;
        }
        if (window.originalClick) {
            HTMLElement.prototype.click = window.originalClick;
        }
    });
    
    console.log('🛑 Button click tracker stopped');
} 