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
    if (captureScreenshot && fs) {
        try {
            await fs.mkdir(screenshotDir, { recursive: true });
        } catch (error) {
            console.warn('Could not create screenshot directory:', error.message);
        }
    }

    // document.addEventListener('close', function(event) {
    //     const element = event.target;
    //     window.trackClick(element, 'global');
    // }, true);
    // async function logEvent(eventData) {
    //     console.log(eventData);
    // }

    /**
     * Logs click information
     * @param {Object} clickData - Data about the clicked element
     */
    async function logClick(clickData) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            clickNumber: ++clickCounter,
            ...clickData
        };
        // const src = '[' + clickData.method + ', ' + clickData.sourceFunc + ']';
        // const src = clickData.method;
        const logString = JSON.stringify(logEntry, null, 2);

        if (enableConsoleLog) {
            // console.log('\n=== BUTTON CLICK TRACKED ' + src + ' ===');
            console.log('\n=== BUTTON CLICK TRACKED ===');
            console.log(logString);
            console.log('=== END TRACKING ===\n');
        }

        if (enableFileLog && fs) {
            try {
                await fs.appendFile(logFilePath, logString + '\n\n');
            } catch (error) {
                console.error('Failed to write to log file:', error.message);
            }
        }
    }

    /**
     * Generates locator suggestions based on element information
     * @param {Object} elementInfo - Element information
     * @returns {Array<string>} Array of locator suggestions
     */
    
    // Expose function to Node.js context
    function generateLocatorSuggestions(elementInfo) {
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

    

    // Inject the tracking script into the page
    await page.evaluateOnNewDocument((trackAllElements) => {
        // Store original methods
        window.originalAddEventListener = EventTarget.prototype.addEventListener;
        window.originalClick = HTMLElement.prototype.click;
        window.clickCounter = 0;
        // window.trackedElements = [];

        // Function to extract element information
        window.extractElementInfo = function(element, method) {
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
                // position: {
                //     x: rect.x,
                //     y: rect.y,
                //     width: rect.width,
                //     height: rect.height
                // },
                // styles: {
                //     backgroundColor: computedStyle.backgroundColor,
                //     color: computedStyle.color,
                //     fontSize: computedStyle.fontSize,
                //     fontWeight: computedStyle.fontWeight,
                //     display: computedStyle.display,
                //     visibility: computedStyle.visibility,
                //     opacity: computedStyle.opacity
                // },
                // isVisible: rect.width > 0 && rect.height > 0 && 
                //            computedStyle.visibility !== 'hidden' && 
                //            computedStyle.display !== 'none',
                isClickable: computedStyle.pointerEvents !== 'none' && 
                            computedStyle.cursor === 'pointer',
                method: method,
                // sourceFunc: 'evaluateOnNewDocument'
            };
        };

        // Function to handle click tracking
        window.trackClick = function(element, method = 'unknown') {
            // Check if we should track this element
            const shouldTrack = trackAllElements || 
                               element.tagName === 'BUTTON' || 
                               element.tagName === 'A' || 
                               element.tagName === 'INPUT' ||
                               element.getAttribute('role') === 'button' || 
                               element.onclick ||
                               element.getAttribute('onclick');

            if (shouldTrack) {
                window.clickCounter++;
                const elementInfo = window.extractElementInfo(element, method);
                // window.trackedElements.push(elementInfo);

                // Log to console for debugging
                console.log('🔍 Click tracked:', {
                    tagName: elementInfo.tagName,
                    textContent: elementInfo.textContent,
                    className: elementInfo.className,
                    id: elementInfo.id,
                    method: elementInfo.method,
                    // sourceFunc: elementInfo.sourceFunc
                });

                // Send to Node.js context
                if (window.logClickToNode) {
                    window.logClickToNode(elementInfo).catch(err => {
                        console.error('Failed to log click to Node.js:', err);
                    });
                }
            }
        };

        // Override addEventListener to track click events
        // EventTarget.prototype.addEventListener = function(type, listener, ...args) {
        //     if (type === 'click') {
        //         const wrappedListener = function(event) {
        //             const element = event.target;
        //             window.trackClick(element, 'addEventListener');
        //             return listener.apply(this, arguments);
        //         };
        //         return window.originalAddEventListener.call(this, type, wrappedListener, ...args);
        //     }
        //     return window.originalAddEventListener.call(this, type, listener, ...args);
        // };

        // Override click method to track programmatic clicks
        HTMLElement.prototype.click = function(...args) {
            const element = this;
            window.trackClick(element, 'programmatic');
            return window.originalClick.apply(this, args);
        };

        // Track onclick assignments
        // Object.defineProperty(HTMLElement.prototype, 'onclick', {
        //     set: function(value) {
        //         this._onclick = value;
        //         if (value) {
        //             this.addEventListener('click', value);
        //         }
        //     },
        //     get: function() {
        //         return this._onclick;
        //     }
        // });

        // Add global click listener as backup
        document.addEventListener('click', function(event) {
            const element = event.target;
            window.trackClick(element, 'global');
        }, true);

        console.log('✅ Button click tracker initialized in page context');
        console.log(`📊 Tracking ${trackAllElements ? 'all clickable elements' : 'buttons only'}`);

    }, trackAllElements);

    await page.exposeFunction('logClickToNode',async (elementInfo) => {
        const locatorSuggestions = generateLocatorSuggestions(elementInfo);
        
        const clickData = {
            url: page.url(),
            elementInfo,
            locatorSuggestions,
            recommendedLocator: locatorSuggestions[0] || 'No specific locator found',
            method: elementInfo.method,
            // sourceFunc: elementInfo.sourceFunc
        };

        await logClick(clickData);
    });
    // Also set up the tracking after page load (in case evaluateOnNewDocument doesn't work)
    await page.evaluate((trackAllElements) => {
        // Check if already initialized
        if (window.trackClick) {
            console.log('Tracker already initialized');
            return;
        }

        // Store original methods
        window.originalAddEventListener = EventTarget.prototype.addEventListener;
        window.originalClick = HTMLElement.prototype.click;
        window.clickCounter = 0;
        window.trackedElements = [];


        // Function to extract element information
        window.extractElementInfo = function(element, method) {
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
                // position: {
                //     x: rect.x,
                //     y: rect.y,
                //     width: rect.width,
                //     height: rect.height
                // },
                // styles: {
                //     backgroundColor: computedStyle.backgroundColor,
                //     color: computedStyle.color,
                //     fontSize: computedStyle.fontSize,
                //     fontWeight: computedStyle.fontWeight,
                //     display: computedStyle.display,
                //     visibility: computedStyle.visibility,
                //     opacity: computedStyle.opacity
                // },
                // isVisible: rect.width > 0 && rect.height > 0 && 
                //            computedStyle.visibility !== 'hidden' && 
                //            computedStyle.display !== 'none',
                isClickable: computedStyle.pointerEvents !== 'none' && 
                            computedStyle.cursor === 'pointer',
                method: method,
                // sourceFunc: 'evaluate'
            };
        };

        // Function to handle click tracking
        window.trackClick = function(element, method = 'unknown') {
            // Check if we should track this element
            const shouldTrack = trackAllElements || 
                               element.tagName === 'BUTTON' || 
                               element.tagName === 'A' || 
                               element.tagName === 'INPUT' ||
                               element.getAttribute('role') === 'button' || 
                               element.onclick ||
                               element.getAttribute('onclick');

            if (shouldTrack) {
                window.clickCounter++;
                const elementInfo = window.extractElementInfo(element, method);
                window.trackedElements.push(elementInfo);
                
                // Log to console for debugging
                console.log('🔍 Click tracked:', {
                    tagName: elementInfo.tagName,
                    textContent: elementInfo.textContent,
                    className: elementInfo.className,
                    id: elementInfo.id,
                    // method: method
                });

                // Send to Node.js context
                if (window.logClickToNode) {
                    window.logClickToNode(elementInfo).catch(err => {
                        console.error('Failed to log click to Node.js:', err);
                    });
                }
            }
        };

        ////EVENT LISTENERS
        // trackClick
        // Override addEventListener to track click events
        // EventTarget.prototype.addEventListener = function(type, listener, ...args) {
        //     if (type === 'click') {
        //         const wrappedListener = function(event) {
        //             const element = event.target;
        //             window.trackClick(element, 'addEventListener');
        //             return listener.apply(this, arguments);
        //         };
        //         return window.originalAddEventListener.call(this, type, wrappedListener, ...args);
        //     }
        //     return window.originalAddEventListener.call(this, type, listener, ...args);
        // };

        // Override click method to track programmatic clicks
        HTMLElement.prototype.click = function(...args) {
            const element = this;
            window.trackClick(element, 'programmatic');
            return window.originalClick.apply(this, args);
        };

        // Track onclick assignments
        // Object.defineProperty(HTMLElement.prototype, 'onclick', {
        //     set: function(value) {
        //         this._onclick = value;
        //         if (value) {
        //             this.addEventListener('click', value);
        //         }
        //     },
        //     get: function() {
        //         return this._onclick;
        //     }
        // });

        // Add global click listener as backup
        document.addEventListener('click', function(event) {
            const element = event.target;
            window.trackClick(element, 'global');
        }, true);

        console.log('✅ Button click tracker initialized in page context');
        console.log(`📊 Tracking ${trackAllElements ? 'all clickable elements' : 'buttons only'}`);

    }, trackAllElements);

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
        // Restore original methods
        if (window.originalAddEventListener) {
            EventTarget.prototype.addEventListener = window.originalAddEventListener;
        }
        if (window.originalClick) {
            HTMLElement.prototype.click = window.originalClick;
        }
        
        // Remove global click listener
        if (window.globalClickHandler) {
            document.removeEventListener('click', window.globalClickHandler, true);
        }
    });
    
    console.log('🛑 Button click tracker stopped');
} 