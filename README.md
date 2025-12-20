# BallsDex Report Pack

> [!NOTE]
> Licensed under Apache 2.0

A standardized BallsDex 3.0 package that allows users to submit reports (bugs, violations, suggestions) to the backend. Administrators can view, manage, and reply to reports via the Django Admin Panel.

> [!NOTE]
> This pioneering initiative supports Laggron's 3.0 vision for Ballsdex, representing a fresh approach to standardised suite integration. I selected the “report” system as the pilot project, as it is the most streamlined system among all my suites. However, as this is the first attempt, please do report any issues encountered!

## Features

*   **Database Integration**: Reports stored using Django Models
*   **Admin Panel Support**: Fully integrated with Django Admin
*   **Dynamic Configuration**: Configure report channel via Admin Panel
*   **Reply System**: Admins can reply to reports, users receive DM notifications
*   **Attachment Support**: Support for file attachments

## Installation

1. **Configure `extra.toml`**  
   
   **If the file doesn't exist:** Create a new file `extra.toml` in your `config` folder under the BallsDex directory.
   
   **If you already have other packages installed:** Simply add the following configuration to your existing `extra.toml` file. Each package is defined by a `[[ballsdex.packages]]` section, so you can have multiple packages installed.
   
   Add the following configuration:

   ```toml
   [[ballsdex.packages]]
   location = "git+https://github.com/Ray-Hsueh/BallsDex-Report-Pack.git"
   path = "report"
   enabled = true
   editable = false
   ```
   
   **Example of multiple packages:**
   ```toml
   # First package
   [[ballsdex.packages]]
   location = "git+https://github.com/example/package1.git"
   path = "package1"
   enabled = true
   editable = false
   
   # Second package (Report Pack)
   [[ballsdex.packages]]
   location = "git+https://github.com/Ray-Hsueh/BallsDex-Report-Pack.git"
   path = "report"
   enabled = true
   editable = false
   ```

2. **Build and Launch**
   ```bash
   docker compose build
   docker compose up -d
   ```

   Migrations will run automatically when the container starts.

## Configuration

1.  Access the Django Admin Panel
2.  Navigate to **Report Configuration**
3.  Add configuration with Discord Channel ID
4.  Enable the configuration

## Usage

### User Command
*   `/report [type] [content] [attachment]`
    *   `type`: Violation, Bug, Suggestion, Other
    *   `content`: Report description
    *   `attachment`: Optional file

### Admin Reply
*   Click **Reply** button on report message in Discord
*   Or edit via Admin Panel
