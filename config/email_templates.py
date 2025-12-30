"""Email templates for PR review notifications with multi-language support."""

# Turkish email templates
EMAIL_TEMPLATES_TR = {
    "subject": "Kod İncelemesi: {pr_title}",
    "body_approved": """Merhaba {pr_author},

"{pr_title}" başlıklı pull request'iniz başarıyla incelendi, sorun bulunamadı.

Pull Request: {pr_url}

İyi çalışmalar,
Otomatik Kod İnceleme Sistemi
""",
    "body_minor": """Merhaba {pr_author},

"{pr_title}" başlıklı pull request'iniz incelendi, küçük iyileştirme önerileri var.

Pull Request: {pr_url}

Detaylar için yukarıdaki linki ziyaret edin.

İyi çalışmalar,
Otomatik Kod İnceleme Sistemi
""",
    "body_critical": """Merhaba {pr_author},

"{pr_title}" başlıklı pull request'iniz incelendi, kritik sorunlar bulundu.

Pull Request: {pr_url}

Detaylar için yukarıdaki linki ziyaret edin.

İyi çalışmalar,
Otomatik Kod İnceleme Sistemi
"""
}

# English email templates
EMAIL_TEMPLATES_EN = {
    "subject": "Code Review: {pr_title}",
    "body_approved": """Hello {pr_author},

Your pull request "{pr_title}" has been successfully reviewed, no issues found.

Pull Request: {pr_url}

Best regards,
Automated Code Review System
""",
    "body_minor": """Hello {pr_author},

Your pull request "{pr_title}" has been reviewed, minor improvement suggestions available.

Pull Request: {pr_url}

Visit the link above for details.

Best regards,
Automated Code Review System
""",
    "body_critical": """Hello {pr_author},

Your pull request "{pr_title}" has been reviewed, critical issues found.

Pull Request: {pr_url}

Visit the link above for details.

Best regards,
Automated Code Review System
"""
}

# Language mapping
EMAIL_TEMPLATES = {
    "tr": EMAIL_TEMPLATES_TR,
    "en": EMAIL_TEMPLATES_EN
}


def get_email_subject(pr_title: str, language: str = "tr") -> str:
    """
    Generate email subject based on language.

    Args:
        pr_title: Pull request title
        language: Language code (tr/en)

    Returns:
        Formatted email subject
    """
    templates = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES_TR)
    return templates["subject"].format(pr_title=pr_title)


def get_email_body(
    pr_title: str,
    pr_author: str,
    pr_url: str,
    severity: str = "minor",
    language: str = "tr"
) -> str:
    """
    Generate email body based on language and severity.

    Args:
        pr_title: Pull request title
        pr_author: Pull request author name
        pr_url: Bitbucket PR URL
        severity: Review severity ('approved', 'minor', or 'critical')
        language: Language code (tr/en)

    Returns:
        Formatted email body
    """
    templates = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES_TR)

    # Select appropriate template based on severity
    body_key = f"body_{severity}"
    if body_key not in templates:
        body_key = "body_minor"  # Default to minor if severity not recognized

    return templates[body_key].format(
        pr_title=pr_title,
        pr_author=pr_author,
        pr_url=pr_url
    )
