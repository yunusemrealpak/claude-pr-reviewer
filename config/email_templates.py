"""Email templates for PR review notifications with multi-language support."""

# Turkish email templates
EMAIL_TEMPLATES_TR = {
    "subject": "Kod İncelemesi: {pr_title}",
    "body": """Merhaba {pr_author},

"{pr_title}" başlıklı pull request'iniz otomatik kod incelemesinden geçmiştir.

Pull Request: {pr_url}

Detaylı inceleme sonuçlarını görmek için yukarıdaki linke tıklayarak Bitbucket'ta PR'ınızı ziyaret edebilirsiniz.

İyi çalışmalar,
Otomatik Kod İnceleme Sistemi
"""
}

# English email templates
EMAIL_TEMPLATES_EN = {
    "subject": "Code Review: {pr_title}",
    "body": """Hello {pr_author},

Your pull request "{pr_title}" has been automatically reviewed.

Pull Request: {pr_url}

Click the link above to view detailed review results on Bitbucket.

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


def get_email_body(pr_title: str, pr_author: str, pr_url: str, language: str = "tr") -> str:
    """
    Generate email body based on language.

    Args:
        pr_title: Pull request title
        pr_author: Pull request author name
        pr_url: Bitbucket PR URL
        language: Language code (tr/en)

    Returns:
        Formatted email body
    """
    templates = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES_TR)
    return templates["body"].format(
        pr_title=pr_title,
        pr_author=pr_author,
        pr_url=pr_url
    )
