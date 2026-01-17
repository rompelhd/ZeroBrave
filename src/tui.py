#!/usr/bin/env python3
"""
ZeroBrave TUI - Interactive Terminal User Interface.

Professional look with ASCII symbols, animations, profiles, and help system.
"""

from dataclasses import dataclass
from typing import Callable
import json
import os
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

# 3D ASCII Banner
BANNER = """[bold cyan]
 ███████╗███████╗██████╗  ██████╗ ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗
 ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝
   ███╔╝ █████╗  ██████╔╝██║   ██║██████╔╝██████╔╝███████║██║   ██║█████╗  
  ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  
 ███████╗███████╗██║  ██║╚██████╔╝██████╔╝██║  ██║██║  ██║ ╚████╔╝ ███████╗
 ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝[/]
                    [bold yellow]Privacy-First Brave Configuration[/]
"""

# Predefined profiles
PROFILES = {
    "strict": {
        "name": "Strict",
        "desc": "Maximum privacy - all protections enabled",
        "categories": ["ai", "privacy", "telemetry", "security", "autofill", "sync", "perms", "brave"]
    },
    "balanced": {
        "name": "Balanced",
        "desc": "Good privacy with some convenience",
        "categories": ["ai", "privacy", "telemetry", "security", "sync", "brave"]
    },
    "minimal": {
        "name": "Minimal",
        "desc": "Basic privacy - only essentials",
        "categories": ["ai", "telemetry", "brave"]
    },
}

# Categories with ASCII tags and help text
CATEGORIES = [
    ("ai", "[AI]", "Disable AI Features", "Leo, Gemini, Lens, AI Writing", 
     "Disables all AI assistants including Leo (Brave's AI), Google Gemini integration, "
     "Google Lens features, and AI-powered writing helpers.", {
        "BraveAIChatEnabled": False,
        "HelpMeWriteSettings": 2,
        "GeminiSettings": 1,
        "GenAiDefaultSettings": 2,
        "GenAiLensOverlaySettings": 2,
        "GenAILocalFoundationalModelSettings": 1,
        "LensRegionSearchEnabled": False,
        "LensDesktopNTPSearchEnabled": False,
        "LensOverlaySettings": 1,
    }),
    ("privacy", "[PRIV]", "Block Tracking", "Cookies, Fingerprinting, WebRTC",
     "Blocks third-party cookies, enables fingerprinting protection, disables Privacy Sandbox, "
     "and prevents WebRTC IP leaks for enhanced privacy.", {
        "BlockThirdPartyCookies": True,
        "PrivacySandboxFingerprintingProtectionEnabled": True,
        "PrivacySandboxPromptEnabled": False,
        "PrivacySandboxAdTopicsEnabled": False,
        "PrivacySandboxSiteEnabledAdsEnabled": False,
        "PrivacySandboxAdMeasurementEnabled": False,
        "WebRtcIPHandling": "disable_non_proxied_udp",
        "WebRtcEventLogCollectionAllowed": False,
    }),
    ("telemetry", "[TEL]", "Disable Telemetry", "Metrics, Reports, Feedback",
     "Completely disables all telemetry, usage statistics, crash reports, "
     "and feedback mechanisms. No data sent to Brave or Google.", {
        "MetricsReportingEnabled": False,
        "DeviceMetricsReportingEnabled": False,
        "UrlKeyedAnonymizedDataCollectionEnabled": False,
        "UrlKeyedMetricsAllowed": False,
        "CloudProfileReportingEnabled": False,
        "CloudReportingEnabled": False,
        "ReportExtensionsAndPluginsData": False,
        "ReportMachineIDData": False,
        "ReportPolicyData": False,
        "ReportUserIDData": False,
        "ReportVersionData": False,
        "UserFeedbackAllowed": False,
        "FeedbackSurveysEnabled": False,
    }),
    ("security", "[SEC]", "Enhanced Security", "Safe Browsing, Updates",
     "Enables Enhanced Safe Browsing (level 2) for better protection against "
     "phishing and malware. Keeps component updates enabled for security patches.", {
        "SafeBrowsingProtectionLevel": 2,
        "SafeBrowsingExtendedReportingEnabled": False,
        "SafeBrowsingSurveysEnabled": False,
        "ComponentUpdatesEnabled": True,
    }),
    ("autofill", "[AUTO]", "Disable Autofill", "Passwords, Payments, Addresses",
     "Disables all autofill features including password manager, credit cards, "
     "and addresses. Use a dedicated password manager instead.", {
        "PaymentMethodQueryEnabled": False,
        "AutofillAddressEnabled": False,
        "AutofillCreditCardEnabled": False,
        "AutofillPredictionSettings": 2,
        "PasswordManagerEnabled": False,
        "PasswordLeakDetectionEnabled": False,
        "PasswordSharingEnabled": False,
    }),
    ("sync", "[SYNC]", "Disable Sync", "No Cloud, No Sign-in",
     "Prevents browser sync and sign-in. Your data stays local and is never "
     "uploaded to Brave's servers.", {
        "SyncDisabled": True,
        "BrowserSignin": 0,
    }),
    ("perms", "[PERM]", "Block Permissions", "Location, Notifications, USB",
     "Sets all sensitive permissions to 'blocked by default'. Sites cannot access "
     "your location, send notifications, or connect to hardware without explicit permission.", {
        "DefaultGeolocationSetting": 2,
        "DefaultNotificationsSetting": 2,
        "DefaultWebBluetoothGuardSetting": 2,
        "DefaultWebUsbGuardSetting": 2,
        "DefaultFileSystemReadGuardSetting": 2,
        "DefaultFileSystemWriteGuardSetting": 2,
        "DefaultLocalFontsSetting": 2,
        "DefaultSensorsSetting": 2,
        "DefaultSerialGuardSetting": 2,
        "DefaultCameraAccessAllowed": False,
        "DefaultMicAccessAllowed": False,
        "ScreenCaptureAllowed": False,
        "AutoplayAllowed": False,
    }),
    ("brave", "[BRAVE]", "Brave Specific", "Rewards, Wallet, VPN, Talk",
     "Disables Brave-specific features: Rewards/BAT tokens, crypto wallet, "
     "VPN promotions, and Brave Talk video calls.", {
        "BraveRewardsDisabled": True,
        "BraveWalletDisabled": True,
        "BraveVPNDisabled": 1,
        "TorDisabled": True,
        "BraveTalkEnabled": False,
    }),
]


class TUI:
    """Professional TUI with profiles, help, and animations."""
    
    def __init__(self, dry_run: bool = False, backup_callback: Callable = None, 
                 apply_callback: Callable = None):
        # Respect NO_COLOR environment variable
        no_color = os.environ.get("NO_COLOR") is not None
        self.console = Console(no_color=no_color)
        self.dry_run = dry_run
        self.backup_callback = backup_callback
        self.apply_callback = apply_callback
        self.enabled = {cat[0]: True for cat in CATEGORIES}
        self.current_profile = "strict"  # Default profile
        self.changes_made = 0  # Track changes this session
    
    def clear(self):
        """Clear screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def animate_banner(self):
        """Animate the banner appearing."""
        banner_plain = """
 ███████╗███████╗██████╗  ██████╗ ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗
 ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝
   ███╔╝ █████╗  ██████╔╝██║   ██║██████╔╝██████╔╝███████║██║   ██║█████╗  
  ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  
 ███████╗███████╗██║  ██║╚██████╔╝██████╔╝██║  ██║██║  ██║ ╚████╔╝ ███████╗
 ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝
                    Privacy-First Brave Configuration
"""
        for line in banner_plain.strip().split('\n'):
            self.console.print(f"[bold cyan]{line}[/]")
            time.sleep(0.04)
    
    def animate_intro(self):
        """Animate program startup."""
        self.clear()
        
        with Progress(
            SpinnerColumn("dots12"),
            TextColumn("[bold cyan]Initializing ZeroBrave...[/]"),
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            time.sleep(0.8)
        
        self.animate_banner()
        time.sleep(0.3)
    
    def animate_exit(self):
        """Animate program exit."""
        self.console.print()
        
        messages = [
            "[dim]Saving configuration...[/]",
            "[dim]Cleaning up...[/]",
            "[bold cyan]Goodbye![/]",
        ]
        
        for msg in messages:
            self.console.print(f"  {msg}")
            time.sleep(0.15)
        
        self.console.print()
        self.console.print(Panel(
            "[bold]Remember to restart Brave for changes to take effect![/]",
            border_style="cyan",
            box=box.ROUNDED,
        ))
        time.sleep(0.3)
    
    def apply_profile(self, profile_key: str):
        """Apply a predefined profile."""
        if profile_key not in PROFILES:
            return
        
        profile = PROFILES[profile_key]
        enabled_cats = profile["categories"]
        
        for cat_key, *_ in CATEGORIES:
            old_state = self.enabled[cat_key]
            new_state = cat_key in enabled_cats
            if old_state != new_state:
                self.changes_made += 1
            self.enabled[cat_key] = new_state
        
        self.current_profile = profile_key
    
    def build_policies(self) -> dict:
        """Build policies dict from enabled categories."""
        result = {}
        for key, tag, name, desc, help_text, policies in CATEGORIES:
            if self.enabled[key]:
                result.update(policies)
        return result
    
    def count_enabled(self) -> tuple[int, int]:
        """Count (enabled_categories, total_policies)."""
        enabled = sum(1 for k, v in self.enabled.items() if v)
        policies = sum(len(cat[5]) for cat in CATEGORIES if self.enabled[cat[0]])
        return enabled, policies
    
    def render_profiles(self) -> Table:
        """Render profile selector."""
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Key", style="bold cyan", width=3)
        table.add_column("Profile", width=12)
        table.add_column("Description", style="dim")
        
        for i, (key, data) in enumerate(PROFILES.items(), 1):
            if key == self.current_profile:
                prefix = "[bold green]>>[/]"
                style = "bold green"
            else:
                prefix = "  "
                style = ""
            table.add_row(f"F{i}", f"[{style}]{data['name']}[/]", data['desc'])
        
        return table
    
    def render_table(self):
        """Render the categories table."""
        table = Table(box=box.DOUBLE_EDGE, show_header=True, header_style="bold white")
        table.add_column("#", style="bold cyan", width=3, justify="center")
        table.add_column("Tag", style="bold", width=8)
        table.add_column("Status", width=8, justify="center")
        table.add_column("Category", width=20)
        table.add_column("Details", style="dim")
        
        for i, (key, tag, name, desc, help_text, policies) in enumerate(CATEGORIES, 1):
            if self.enabled[key]:
                status = "[bold green]++ ON[/]"
                tag_style = f"[cyan]{tag}[/]"
            else:
                status = "[dim red]-- OFF[/]"
                tag_style = f"[dim]{tag}[/]"
            
            table.add_row(str(i), tag_style, status, name, desc)
        
        return table
    
    def render(self, animate: bool = False):
        """Render the main screen."""
        self.clear()
        
        if animate:
            self.animate_banner()
        else:
            self.console.print(BANNER)
        
        enabled_cats, total_policies = self.count_enabled()
        
        # Status bar with profile and changes indicator
        profile_name = PROFILES[self.current_profile]["name"]
        status_parts = [
            f"[bold]Profile: {profile_name}[/]",
            f"[bold]Categories: {enabled_cats}/8[/]",
            f"[bold]Policies: {total_policies}[/]",
        ]
        
        if self.changes_made > 0:
            status_parts.append(f"[yellow]Changes: {self.changes_made}[/]")
        
        if self.dry_run:
            status_parts.insert(0, "[bold yellow]>> DRY-RUN <<[/]")
        
        self.console.print(Panel(" | ".join(status_parts), box=box.MINIMAL))
        self.console.print()
        
        # Profiles bar
        self.console.print("[bold]Profiles:[/] ", end="")
        for key, data in PROFILES.items():
            letter = key[0].upper()  # S, B, M
            if key == self.current_profile:
                self.console.print(f"[bold green][{letter}] {data['name']}[/]", end="  ")
            else:
                self.console.print(f"[dim][{letter}] {data['name']}[/]", end="  ")
        self.console.print("\n")
        
        # Categories table
        self.console.print(self.render_table())
        self.console.print()
        
        # Commands
        cmd_panel = Panel(
            "[cyan]1-8[/] Toggle  |  "
            "[cyan]S[/]trict [cyan]B[/]alanced [cyan]M[/]inimal  |  "
            "[cyan]?[/] Help  |  "
            "[cyan]A[/]ll  |  "
            "[cyan]P[/]review  |  "
            "[green]ENTER[/] Apply  |  "
            "[red]Q[/]uit",
            title="[bold]Commands[/]",
            border_style="dim cyan",
            box=box.ROUNDED,
        )
        self.console.print(cmd_panel)
        self.console.print()
    
    def show_help(self, category_num: int = None):
        """Show contextual help."""
        self.clear()
        self.console.print(BANNER)
        
        if category_num and 1 <= category_num <= 8:
            # Show specific category help
            key, tag, name, desc, help_text, policies = CATEGORIES[category_num - 1]
            
            self.console.print(Panel(
                f"[bold]{tag} {name}[/]\n\n"
                f"{help_text}\n\n"
                f"[dim]Policies ({len(policies)}):[/]\n" +
                "\n".join(f"  • {p}" for p in list(policies.keys())[:10]) +
                ("\n  ..." if len(policies) > 10 else ""),
                title=f"[bold cyan]Help: Category {category_num}[/]",
                border_style="cyan",
            ))
        else:
            # Show general help
            help_text = """
[bold cyan]ZeroBrave TUI - Help[/]

[bold]Navigation:[/]
  [cyan]1-8[/]      Toggle individual categories ON/OFF
  [cyan]S[/]        Apply 'Strict' profile (maximum privacy)
  [cyan]B[/]        Apply 'Balanced' profile (privacy + convenience)
  [cyan]M[/]        Apply 'Minimal' profile (essential only)
  [cyan]A[/]        Toggle ALL categories ON/OFF
  [cyan]P[/]        Preview JSON policies
  [cyan]ENTER[/]    Apply policies to Brave
  [cyan]Q[/]        Quit without applying
  [cyan]?[/]        Show this help
  [cyan]?1-8[/]     Show help for specific category

[bold]Profiles:[/]
  [green]Strict[/]    - All 8 categories enabled (maximum privacy)
  [yellow]Balanced[/]  - 6 categories (keeps autofill, permissions optional)
  [dim]Minimal[/]   - 3 categories (AI, telemetry, Brave-specific only)

[bold]Tips:[/]
  • Changes require restarting Brave to take effect
  • Use --dry-run to preview without applying
  • Policies are enforced and cannot be changed by users
"""
            self.console.print(Panel(help_text, title="[bold]Help[/]", border_style="cyan"))
        
        self.console.print()
        input("Press ENTER to go back...")
    
    def show_preview(self):
        """Show JSON preview with animation."""
        self.clear()
        self.console.print(BANNER)
        
        policies = self.build_policies()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]Generating preview..."),
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            time.sleep(0.5)
        
        json_str = json.dumps(policies, indent=2)
        
        self.console.print(Panel(
            f"[cyan]{json_str}[/]",
            title=f"[bold yellow]<< {len(policies)} Policies >>[/]",
            border_style="yellow",
            box=box.DOUBLE,
        ))
        self.console.print()
        input("Press ENTER to go back...")
    
    def apply(self):
        """Apply policies with progress animation."""
        policies = self.build_policies()
        _, total = self.count_enabled()
        
        self.console.print()
        
        if self.dry_run:
            self.console.print("[bold yellow]>> DRY-RUN: Simulating apply...[/]\n")
        
        with Progress(
            SpinnerColumn("dots"),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[bold cyan]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("Applying policies...", total=100)
            
            for i in range(100):
                time.sleep(0.015)
                progress.update(task, advance=1)
                
                if i == 30:
                    progress.update(task, description="Writing configuration...")
                elif i == 60:
                    progress.update(task, description="Validating policies...")
                elif i == 90:
                    progress.update(task, description="Finalizing...")
        
        if self.apply_callback:
            try:
                self.apply_callback(policies, self.dry_run)
                self.console.print()
                self.console.print(Panel(
                    "[bold green]>>> SUCCESS <<<[/]\n\n"
                    f"Applied [cyan]{total}[/] policies.\n"
                    "[dim]Restart Brave for changes to take effect.[/]",
                    border_style="green",
                    box=box.DOUBLE,
                ))
                self.changes_made = 0  # Reset changes counter
            except Exception as e:
                self.console.print(f"\n[bold red]ERROR:[/] {e}")
        else:
            self.console.print("\n[yellow]Note: No apply callback configured[/]")
        
        self.console.print()
        input("Press ENTER to continue...")
    
    def toggle_with_feedback(self, idx: int):
        """Toggle a category with visual feedback."""
        if 1 <= idx <= 8:
            key = CATEGORIES[idx - 1][0]
            self.enabled[key] = not self.enabled[key]
            self.changes_made += 1
            self.current_profile = "custom"  # No longer matches a profile
            
            status = "[green]ON[/]" if self.enabled[key] else "[red]OFF[/]"
            self.console.print(f"  {CATEGORIES[idx - 1][1]} -> {status}", highlight=False)
            time.sleep(0.1)
    
    def run(self):
        """Main loop."""
        self.animate_intro()
        time.sleep(0.2)
        
        first_render = False
        
        while True:
            self.render(animate=first_render)
            first_render = False
            
            try:
                choice = input(">>> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                self.animate_exit()
                return
            
            if choice == 'q':
                self.animate_exit()
                return
            elif choice == 'p':
                self.show_preview()
            elif choice == '' or choice == 'enter':
                self.apply()
            elif choice == '?':
                self.show_help()
            elif choice.startswith('?') and len(choice) == 2 and choice[1].isdigit():
                self.show_help(int(choice[1]))
            elif choice == 'a':
                if any(self.enabled.values()):
                    for k in self.enabled:
                        self.enabled[k] = False
                else:
                    for k in self.enabled:
                        self.enabled[k] = True
                self.changes_made += 1
                self.current_profile = "custom"
            elif choice == 's':
                self.apply_profile("strict")
            elif choice == 'b':
                self.apply_profile("balanced")
            elif choice == 'm':
                self.apply_profile("minimal")
            elif choice.isdigit():
                self.toggle_with_feedback(int(choice))


def run_tui(dry_run: bool = False, backup_callback: Callable = None, 
            apply_callback: Callable = None):
    """Entry point."""
    tui = TUI(dry_run=dry_run, backup_callback=backup_callback, 
              apply_callback=apply_callback)
    tui.run()


if __name__ == "__main__":
    run_tui(dry_run=True)
