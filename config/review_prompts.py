"""Review prompt templates for Claude Code CLI with multi-language support."""

# Severity labels used in review output
SEVERITY_LABELS = {
    "approved": "🟢 LGTM",
    "minor": "🟡 Minor Issues",
    "critical": "🔴 Needs Review"
}

# Turkish prompts
PROMPTS_TR = {
    "review_prompt": """Bu Flutter/Dart pull request'ini kod kalitesi açısından incele.

## PR'daki Commit'ler:
{commit_summary}

## Değişen Dosyalar:
{files_summary}

## Kod Diff:
```diff
{diff_content}
```

## İnceleme Kriterleri:

### 1. Presentation Katmanı (UI/Cubit)
- **State Management**: State management Cubit/State pattern ile yapılmış mı?
- **Cubit Sorumlulukları**: Cubit içerisinde business logic var mı? (Cubit'in tek görevi UI ile usecase'ler arasında köprü görevi görmek ve state'i güncellemek olmalı)
- **UI Temizliği**: UI sayfalarında uzun kodlar var mı? Componentlere ayrılmış mı?
- **Freezed Kullanımı**: State'ler freezed ile kurgulanmış mı?
- **Design System**: Projedeki design_system kullanılmış mı? Design system'da olan yapılar yeniden yazılmamış mı?
- **Widget Best Practices**: const constructor'lar kullanılmış mı?

### 2. Domain Katmanı (Entities/UseCases/Repositories)
- **Entity Yapısı**: Entity'ler Equatable ile sarmalanmış mı?
- **UseCase Pattern**: UseCase'ler UseCase<T,R> veya UseCaseWithoutParams<T> ile sarmalanmış mı?
- **Validation**: UseCase'ler gerekli validation kontrollerini yapıyor mu?
- **Params Konumu**: UseCase'lerin ihtiyaç duyduğu params modelleri, usecase dosyasının içinde üstte oluşturulmuş mu?
- **Dependency Injection**: Dependency injection düzgün uygulanmış mı?

### 3. Data Katmanı (Models/Repositories/DataSources)
- **Model-Entity Ayrımı**: Modeller Entity'lerden extend edilmemiş mi? (Modeller ayrı, Entity'ler ayrı olmalı)
- **Error Handling**: Repository'ler projedeki error handler ile kullanılmış mı?
- **Exception Handling**: Remote data source'lar try-catch mekanizmasını düzgün kullanmış mı?
- **Repository Pattern**: Repository pattern'e uyulmuş mu?

### 4. Dart Conventions & Performans
- **Null Safety**: Null safety düzgün kullanılmış mı?
- **Naming**: effective_dart kurallarına ve naming convention'lara uyulmuş mu?
- **Rebuild Optimizasyonu**: Gereksiz rebuild var mı?
- **Memory Management**: Memory leak riski var mı?
- **Async Handling**: Async handling doğru mu?

### 5. Güvenlik
- **Input Validation**: Input validation yapılmış mı?
- **Data Exposure**: Hassas veri exposure riski var mı?

## Çıktı Formatı:

MUTLAKA aşağıdaki formatta yanıt ver:

### Severity Label
Değişikliklerin genel durumuna göre SADECE BİRİNİ seç:
- 🟢 LGTM - Ciddi sorun yok, kod kalitesi iyi
- 🟡 Minor Issues - Küçük iyileştirmeler önerilir ama kritik değil
- 🔴 Needs Review - Kritik sorunlar var, merge öncesi düzeltilmeli

### Özet
2-3 cümlelik genel değerlendirme.

### Bulgular
Varsa sorunları katman bazlı ve önem derecesine göre listele:

**Presentation Katmanı:**
- Cubit'te business logic kullanımı (KRİTİK)
- Freezed kullanılmamış state'ler (YÜKSEK)
- Design system yerine custom widget yazımı (YÜKSEK)
- Uzun UI dosyaları, componentlere ayrılmamış kod (ORTA)

**Domain Katmanı:**
- Entity'ler Equatable kullanmıyor (YÜKSEK)
- UseCase pattern'e uyulmuyor (KRİTİK)
- Validation eksik (YÜKSEK)
- Params modelleri yanlış konumda (ORTA)

**Data Katmanı:**
- Model'ler Entity'den extend ediliyor (KRİTİK)
- Error handler kullanılmıyor (YÜKSEK)
- Try-catch mekanizması eksik/hatalı (YÜKSEK)

**Diğer:**
- **KRİTİK**: Merge öncesi mutlaka düzeltilmeli
- **YÜKSEK**: Düzeltilmesi önerilir
- **ORTA**: İyileştirme önerisi
- **DÜŞÜK**: Stil/convention önerisi

### Dosya Bazlı Öneriler
Spesifik dosya ve satır önerileri ile birlikte hangi katman kuralının ihlal edildiğini belirt.
Örnekler vererek nasıl düzeltilmesi gerektiğini göster.

ÖZEL UYARI: Eğer design_system'da olan bir component yeniden yazılmışsa, mutlaka bunu vurgula ve design_system'daki ilgili componenti öner.

Yapıcı ve spesifik ol. Gereksiz detaya girme, en önemli konulara odaklan.""",

    "comment_header": "## 🤖 Otomatik Kod İncelemesi",
    "comment_footer": "*Bu inceleme Claude Code CLI tarafından otomatik oluşturulmuştur. Önerileri değerlendirirken kendi muhakemenizi kullanın.*"
}

# English prompts
PROMPTS_EN = {
    "review_prompt": """Review this Flutter/Dart pull request for code quality.

## Commits in PR:
{commit_summary}

## Changed Files:
{files_summary}

## Code Diff:
```diff
{diff_content}
```

## Review Criteria:

### 1. Presentation Layer (UI/Cubit)
- **State Management**: Is state management implemented with Cubit/State pattern?
- **Cubit Responsibilities**: Does Cubit contain business logic? (Cubit's only responsibility should be bridging UI with usecases and updating state)
- **UI Cleanliness**: Are UI pages too long? Are they separated into components?
- **Freezed Usage**: Are states structured with freezed?
- **Design System**: Is the project's design_system being used? Are design system components being rewritten unnecessarily?
- **Widget Best Practices**: Are const constructors used?

### 2. Domain Layer (Entities/UseCases/Repositories)
- **Entity Structure**: Are entities wrapped with Equatable?
- **UseCase Pattern**: Are usecases wrapped with UseCase<T,R> or UseCaseWithoutParams<T>?
- **Validation**: Do usecases perform necessary validation checks?
- **Params Location**: Are usecase params models created at the top of the usecase file?
- **Dependency Injection**: Is dependency injection properly implemented?

### 3. Data Layer (Models/Repositories/DataSources)
- **Model-Entity Separation**: Do models NOT extend from entities? (Models and Entities should be separate)
- **Error Handling**: Do repositories use the project's error handler?
- **Exception Handling**: Do remote data sources properly use try-catch mechanism?
- **Repository Pattern**: Is repository pattern followed?

### 4. Dart Conventions & Performance
- **Null Safety**: Is null safety properly used?
- **Naming**: Are effective_dart rules and naming conventions followed?
- **Rebuild Optimization**: Are there unnecessary rebuilds?
- **Memory Management**: Is there memory leak risk?
- **Async Handling**: Is async handling correct?

### 5. Security
- **Input Validation**: Is input validation done?
- **Data Exposure**: Is there sensitive data exposure risk?

## Output Format:

You MUST respond in the following format:

### Severity Label
Based on overall changes, select ONLY ONE:
- 🟢 LGTM - No serious issues, code quality is good
- 🟡 Minor Issues - Small improvements suggested but not critical
- 🔴 Needs Review - Critical issues found, must fix before merge

### Summary
2-3 sentence overall assessment.

### Findings
List issues by layer and severity if any:

**Presentation Layer:**
- Business logic in Cubit (CRITICAL)
- States not using freezed (HIGH)
- Custom widgets instead of design_system (HIGH)
- Long UI files, code not separated into components (MEDIUM)

**Domain Layer:**
- Entities not using Equatable (HIGH)
- UseCase pattern not followed (CRITICAL)
- Missing validation (HIGH)
- Params models in wrong location (MEDIUM)

**Data Layer:**
- Models extending from Entities (CRITICAL)
- Error handler not used (HIGH)
- Try-catch mechanism missing/incorrect (HIGH)

**Other:**
- **CRITICAL**: Must fix before merge
- **HIGH**: Should fix
- **MEDIUM**: Improvement suggestion
- **LOW**: Style/convention suggestion

### File-Specific Suggestions
Provide specific file and line suggestions along with which layer rule is violated.
Show how to fix with examples.

SPECIAL WARNING: If a component from design_system is being rewritten, highlight this and suggest the relevant component from design_system.

Be constructive and specific. Avoid unnecessary details, focus on the most important issues.""",

    "comment_header": "## 🤖 Automatic Code Review",
    "comment_footer": "*This review was automatically generated by Claude Code CLI. Use your own judgment when evaluating suggestions.*"
}

# Language mapping
PROMPTS = {
    "tr": PROMPTS_TR,
    "en": PROMPTS_EN
}


def get_review_prompt(
    commit_summary: str,
    files_summary: str,
    diff_content: str,
    language: str = "tr"
) -> str:
    """
    Generate the review prompt for Flutter/Dart code.

    Args:
        commit_summary: Summary of commits in the PR
        files_summary: Summary of file changes
        diff_content: Raw diff content
        language: Language code (tr/en)

    Returns:
        Complete prompt string for Claude
    """
    prompts = PROMPTS.get(language, PROMPTS_TR)

    # Escape curly braces to prevent format string errors
    # Dart/Flutter code and commit messages often contain {} which conflicts with Python's format()
    safe_commit_summary = commit_summary.replace("{", "{{").replace("}", "}}")
    safe_files_summary = files_summary.replace("{", "{{").replace("}", "}}")
    safe_diff_content = diff_content.replace("{", "{{").replace("}", "}}")

    return prompts["review_prompt"].format(
        commit_summary=safe_commit_summary,
        files_summary=safe_files_summary,
        diff_content=safe_diff_content
    )


def get_comment_header(language: str = "tr") -> str:
    """Get localized comment header."""
    prompts = PROMPTS.get(language, PROMPTS_TR)
    return prompts["comment_header"]


def get_comment_footer(language: str = "tr") -> str:
    """Get localized comment footer."""
    prompts = PROMPTS.get(language, PROMPTS_TR)
    return prompts["comment_footer"]
