"""Playwright-based menu and page testing for Drupal sites."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
import asyncio

from .config import load_config
from .logger import setup_logger
from .utils import write_json


async def test_menu_links() -> Path:
    """Test all menu links on the homepage using Playwright."""
    config = load_config()
    logger = setup_logger("menu_testing", config.logs_dir)
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed. Install with: pip install playwright")
        raise RuntimeError("Playwright required for menu testing")
    
    logger.info("Starting menu link testing with Playwright")
    logger.info("Site URL: %s", config.site_url)
    
    menu_results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "site_url": config.site_url,
        "total_links_found": 0,
        "total_links_tested": 0,
        "successful_links": 0,
        "failed_links": 0,
        "links": [],
        "errors": [],
    }
    
    async with async_playwright() as p:
        # Launch browser
        logger.info("Launching Chromium browser (headless)")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            ignore_https_errors=True,  # For DDEV self-signed certs
        )
        page = await context.new_page()
        
        try:
            # Load homepage
            logger.info("Loading homepage: %s", config.site_url)
            response = await page.goto(config.site_url, wait_until="networkidle")
            
            if response is None or response.status >= 400:
                logger.error("Failed to load homepage: status %s", response.status if response else "None")
                menu_results["errors"].append(f"Homepage load failed: {response.status if response else 'No response'}")
            else:
                logger.info("Homepage loaded successfully: %s", response.status)
            
            # Extract menu links
            logger.info("Extracting menu links from homepage")
            menu_selectors = [
                "nav a",
                ".menu a",
                ".navbar a",
                ".navigation a",
                "header a",
                "[role='navigation'] a",
            ]
            
            links_found = set()
            for selector in menu_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute("href")
                        if href and href.startswith(("/", "http")):
                            # Convert relative to absolute
                            if href.startswith("/"):
                                full_url = config.site_url.rstrip("/") + href
                            else:
                                full_url = href
                            
                            # Only test same-domain links
                            if config.site_url.rstrip("/") in full_url:
                                links_found.add(full_url)
                except Exception as e:
                    logger.warning("Error extracting links from selector %s: %s", selector, str(e))
            
            menu_results["total_links_found"] = len(links_found)
            logger.info("Found %d unique menu links", len(links_found))
            
            # Test each link
            logger.info("Testing %d menu links", len(links_found))
            for link_url in sorted(links_found):
                try:
                    logger.info("Testing link: %s", link_url)
                    link_response = await page.goto(link_url, wait_until="networkidle", timeout=30000)
                    
                    status = link_response.status if link_response else 0
                    title = await page.title()
                    
                    menu_results["total_links_tested"] += 1
                    
                    link_result = {
                        "url": link_url,
                        "status": status,
                        "title": title,
                        "success": status < 400,
                    }
                    
                    if status < 400:
                        menu_results["successful_links"] += 1
                        logger.info("✅ Link OK: %s (Status: %s)", link_url, status)
                    else:
                        menu_results["failed_links"] += 1
                        logger.warning("❌ Link Failed: %s (Status: %s)", link_url, status)
                    
                    menu_results["links"].append(link_result)
                    
                except asyncio.TimeoutError:
                    logger.warning("⏱️ Link timeout: %s", link_url)
                    menu_results["total_links_tested"] += 1
                    menu_results["failed_links"] += 1
                    menu_results["links"].append({
                        "url": link_url,
                        "status": 0,
                        "title": "Timeout",
                        "success": False,
                        "error": "Page load timeout (30s)",
                    })
                except Exception as e:
                    logger.error("Error testing link %s: %s", link_url, str(e))
                    menu_results["total_links_tested"] += 1
                    menu_results["failed_links"] += 1
                    menu_results["links"].append({
                        "url": link_url,
                        "status": 0,
                        "title": "Error",
                        "success": False,
                        "error": str(e),
                    })
            
            # Generate summary
            logger.info("Menu testing complete:")
            logger.info("  Total links found: %d", menu_results["total_links_found"])
            logger.info("  Total links tested: %d", menu_results["total_links_tested"])
            logger.info("  Successful: %d", menu_results["successful_links"])
            logger.info("  Failed: %d", menu_results["failed_links"])
            
            if menu_results["failed_links"] > 0:
                logger.warning("⚠️ %d menu links failed", menu_results["failed_links"])
            else:
                logger.info("✅ All menu links passed!")
            
        finally:
            await context.close()
            await browser.close()
    
    # Write report
    report_path = config.reports_dir / "menu-check.json"
    write_json(report_path, menu_results)
    logger.info("Menu testing report written to %s", report_path)
    
    return report_path


def run_menu_tests() -> Path:
    """Synchronous wrapper for async menu testing."""
    return asyncio.run(test_menu_links())


if __name__ == "__main__":
    run_menu_tests()
