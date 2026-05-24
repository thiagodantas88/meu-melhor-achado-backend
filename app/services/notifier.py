"""
Email notifications for Meu Melhor Achado scraper runs.

Uses the Resend HTTP API so it works on Railway without SMTP ports.
"""

import logging
import os
from datetime import datetime

import resend

logger = logging.getLogger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY", "")

NOTIFY_EMAILS = [
    email.strip()
    for email in os.getenv("NOTIFY_EMAILS", "").split(",")
    if email.strip()
]
NOTIFY_FROM = os.getenv("NOTIFY_FROM", "onboarding@resend.dev")


def _format_price(value) -> str:
    if not value:
        return "-"
    return f"R$ {value:.2f}".replace(".", ",")


def _build_html(
    run_id: str,
    deals: list[dict],
    comparisons: list[dict],
    errors: int,
    fallback_count: int,
) -> str:
    by_category: dict[str, list[dict]] = {}
    for deal in deals:
        by_category.setdefault(deal.get("category", "outros"), []).append(deal)

    category_icons = {
        "tecnologia": "💻",
        "casa": "🏠",
        "carro": "🚗",
        "home-office": "🖥️",
        "bebidas": "🍷",
        "moda": "👗",
    }

    deals_html = ""
    for category, items in by_category.items():
        icon = category_icons.get(category, "🛒")
        deals_html += (
            f"<h3 style='color:#1E3A5F;margin:16px 0 8px'>{icon} "
            f"{category.title()} ({len(items)})</h3>"
            "<ul style='margin:0;padding-left:20px'>"
        )
        for deal in items[:5]:
            discount = (
                f" <span style='color:#D4A373'>(-{deal['discount_pct']}%)</span>"
                if deal.get("discount_pct")
                else ""
            )
            source = (deal.get("source") or "").upper()
            deals_html += (
                "<li style='margin-bottom:4px'>"
                f"<a href='{deal.get('affiliate_url', '#')}' style='color:#1E3A5F'>"
                f"{deal.get('product_name', '-')}"
                "</a>"
                f" - <strong>{_format_price(deal.get('deal_price'))}</strong>{discount} "
                f"<small style='color:#6B7280'>[{source}]</small>"
                "</li>"
            )
        if len(items) > 5:
            deals_html += f"<li style='color:#6B7280'>... e mais {len(items) - 5} ofertas</li>"
        deals_html += "</ul>"

    if not deals_html:
        deals_html = "<p style='color:#6B7280'>Nenhuma oferta publicada nesta rodada.</p>"

    comparisons_html = ""
    for comparison in comparisons:
        product_a = comparison.get("product_a", {})
        product_b = comparison.get("product_b", {})
        comparisons_html += (
            "<div style='background:#F5EFE6;border-radius:8px;padding:12px;margin-bottom:8px'>"
            f"<strong style='color:#1E3A5F'>{comparison.get('title', '')}</strong><br>"
            f"<small>{product_a.get('name', '-')} ({product_a.get('price', '-')}) vs "
            f"{product_b.get('name', '-')} ({product_b.get('price', '-')})</small>"
            "</div>"
        )
    if not comparisons_html:
        comparisons_html = "<p style='color:#6B7280'>Nenhum comparativo gerado nesta rodada.</p>"

    alerts = ""
    if errors > 0:
        alerts += f"<p style='color:#c0392b'>⚠️ {errors} erro(s) durante a busca.</p>"
    if fallback_count > 0:
        alerts += (
            f"<p style='color:#e67e22'>ℹ️ {fallback_count} oferta(s) vieram do fallback "
            "(sem preço novo capturado da loja).</p>"
        )

    now = datetime.now().strftime("%d/%m/%Y às %H:%M")

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#2D2D2D">
      <div style="background:#1E3A5F;padding:24px;border-radius:12px 12px 0 0">
        <h1 style="color:#fff;margin:0;font-size:20px">🔍 Meu Melhor Achado - Relatório</h1>
        <p style="color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:13px">
          Rodada: {run_id} &nbsp;|&nbsp; {now}
        </p>
      </div>
      <div style="background:#fff;padding:24px;border:1px solid #E8E0D5;border-top:none">
        <div style="display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap">
          <div style="background:#F5EFE6;border-radius:8px;padding:12px 20px;text-align:center;flex:1">
            <div style="font-size:28px;font-weight:bold;color:#1E3A5F">{len(deals)}</div>
            <div style="font-size:12px;color:#6B7280">Ofertas publicadas</div>
          </div>
          <div style="background:#F5EFE6;border-radius:8px;padding:12px 20px;text-align:center;flex:1">
            <div style="font-size:28px;font-weight:bold;color:#1E3A5F">{len(comparisons)}</div>
            <div style="font-size:12px;color:#6B7280">Comparativos</div>
          </div>
          <div style="background:#F5EFE6;border-radius:8px;padding:12px 20px;text-align:center;flex:1">
            <div style="font-size:28px;font-weight:bold;color:{'#c0392b' if errors else '#27ae60'}">{errors}</div>
            <div style="font-size:12px;color:#6B7280">Erros</div>
          </div>
        </div>
        {alerts}
        <h2 style="color:#1E3A5F;font-size:16px;border-bottom:2px solid #D4A373;padding-bottom:8px">
          📊 Comparativos do dia
        </h2>
        {comparisons_html}
        <h2 style="color:#1E3A5F;font-size:16px;border-bottom:2px solid #D4A373;padding-bottom:8px;margin-top:24px">
          🛒 Ofertas publicadas
        </h2>
        {deals_html}
        <div style="margin-top:24px;padding-top:16px;border-top:1px solid #E8E0D5">
          <a href="https://meumelhorachado.com.br/ofertas"
             style="background:#D4A373;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:bold">
            Ver ofertas →
          </a>
        </div>
      </div>
      <div style="background:#F5EFE6;padding:12px 24px;border-radius:0 0 12px 12px;font-size:11px;color:#6B7280;text-align:center">
        Meu Melhor Achado · meumelhorachado.com.br · Email automatico
      </div>
    </div>
    """


def send_run_report(
    run_id: str,
    deals: list[dict],
    comparisons: list[dict],
    errors: int = 0,
    fallback_count: int = 0,
) -> None:
    if not NOTIFY_EMAILS:
        logger.warning("NOTIFY_EMAILS nao configurado; email nao enviado")
        return

    if not resend.api_key:
        logger.warning("RESEND_API_KEY nao configurado; email nao enviado")
        return

    subject = f"[Meu Melhor Achado] Rodada {run_id} - {len(deals)} ofertas"
    if errors > 0:
        subject += f" - {errors} erro(s)"

    try:
        resend.Emails.send(
            {
                "from": NOTIFY_FROM,
                "to": NOTIFY_EMAILS,
                "subject": subject,
                "html": _build_html(run_id, deals, comparisons, errors, fallback_count),
            }
        )
        logger.info("Email enviado para: %s", ", ".join(NOTIFY_EMAILS))
    except Exception as exc:
        logger.error("Erro ao enviar email de notificacao: %s", exc)
