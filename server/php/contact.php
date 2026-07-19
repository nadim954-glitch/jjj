<?php
/**
 * SANI Trocknung – Kontaktformular-Mailhandler (OPTIONALES Modul).
 * Aktivierung erst nach Hosting-Klärung (PH-08) und Konfiguration von config.php.
 *
 * Sicherheit / Regeln (Masterdokument Kap. 18.5, 19.2):
 *  - Nimmt nur POST von eigener Domain an (Origin/Referer-Plausibilität).
 *  - Serverseitige Validierung identisch zum Frontend.
 *  - Spam: Honeypot + Zeitfalle + einfaches Rate-Limit.
 *  - Header-Injection verhindern (CR/LF entfernen); From fest, Nutzer nur Reply-To.
 *  - Empfänger aus config.php (nicht aus dem Request).
 *  - Keine Protokollierung von Formularinhalten.
 */

declare(strict_types=1);

$configFile = __DIR__ . '/config.php';
if (!is_file($configFile)) {
    respond(false, ['_' => 'Konfiguration fehlt.'], 500);
}
$config = require $configFile;

// --- Nur POST -------------------------------------------------------------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    respond(false, ['_' => 'Methode nicht erlaubt.'], 405);
}

// --- Origin/Referer-Plausibilität ----------------------------------------
$allowedHost = $config['allowed_host'] ?? '';
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
if ($allowedHost !== '' && $origin !== '' && stripos($origin, $allowedHost) === false) {
    respond(false, ['_' => 'Ungültige Herkunft.'], 403);
}

// --- Content-Length-Limit -------------------------------------------------
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 20000) {
    respond(false, ['_' => 'Anfrage zu groß.'], 413);
}

// --- Spam: Honeypot -------------------------------------------------------
if (trim((string) ($_POST['website'] ?? '')) !== '') {
    // Bot: still verwerfen, Erfolg vortäuschen.
    respond(true, [], 200);
}

// --- Spam: Zeitfalle (Absenden < 3s = verwerfen) --------------------------
$ts = (int) ($_POST['ts'] ?? 0);
$nowMs = (int) (microtime(true) * 1000);
if ($ts > 0 && ($nowMs - $ts) < 3000) {
    respond(true, [], 200);
}

// --- Rate-Limit je IP (datei-basiert, ohne Personenbezug) -----------------
if (!rateLimitOk($config['rate_limit_dir'] ?? sys_get_temp_dir(), (int) ($config['rate_limit_seconds'] ?? 30))) {
    respond(false, ['_' => 'Bitte warten Sie einen Moment und versuchen Sie es erneut.'], 429);
}

// --- Eingaben einlesen + bereinigen --------------------------------------
$vorname     = clean($_POST['vorname'] ?? '');
$nachname    = clean($_POST['nachname'] ?? '');
$telefon     = clean($_POST['telefon'] ?? '');
$email       = clean($_POST['email'] ?? '');
$adresse     = clean($_POST['adresse'] ?? '');
$schadensart = clean($_POST['schadensart'] ?? '');
$nachricht   = clean($_POST['nachricht'] ?? '', 2000);
$kontaktart  = clean($_POST['kontaktart'] ?? '');
$datenschutz = isset($_POST['datenschutz']);

// --- Validierung (identisch zum Frontend, Kap. 19.2) ----------------------
$errors = [];
if (mb_strlen($vorname) < 2 || mb_strlen($vorname) > 60)  $errors['vorname'] = 'Bitte geben Sie Ihren Vornamen ein.';
if (mb_strlen($nachname) < 2 || mb_strlen($nachname) > 60) $errors['nachname'] = 'Bitte geben Sie Ihren Nachnamen ein.';

$telOk  = $telefon !== '' && preg_match('/^[+\d][\d\s\/()-]*$/', $telefon) && countDigits($telefon) >= 6 && countDigits($telefon) <= 20;
$mailOk = $email !== '' && filter_var($email, FILTER_VALIDATE_EMAIL) && mb_strlen($email) <= 120;
if ($telefon !== '' && !$telOk) $errors['telefon'] = 'Bitte geben Sie eine gültige Telefonnummer ein.';
if ($email !== '' && !$mailOk)  $errors['email'] = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.';
if (!$telOk && !$mailOk) {
    $errors['telefon'] = 'Bitte geben Sie Telefonnummer oder E-Mail-Adresse an.';
    $errors['email']   = 'Bitte geben Sie Telefonnummer oder E-Mail-Adresse an.';
}

$artWhitelist = ['Akuter Wasserschaden', 'Verdacht auf Leckage', 'Feuchtigkeit oder Schimmel', 'Trocknung angefragt', 'Wiederherstellung', 'Sonstiges'];
if (!in_array($schadensart, $artWhitelist, true)) $errors['schadensart'] = 'Bitte wählen Sie die Art des Schadens aus.';

$kontaktWhitelist = ['', 'Telefon', 'E-Mail', 'WhatsApp'];
if (!in_array($kontaktart, $kontaktWhitelist, true)) $kontaktart = '';

if (mb_strlen($adresse) > 160)   $errors['adresse'] = 'Adresse zu lang.';
if (!$datenschutz)               $errors['datenschutz'] = 'Bitte bestätigen Sie die Datenschutzerklärung.';

if (!empty($errors)) {
    respond(false, $errors, 422);
}

// --- E-Mail zusammenbauen -------------------------------------------------
$to      = $config['recipient'];          // [PH-11] aus config.php, nie aus Request
$from    = $config['from'];               // fester Domain-Absender
$subject = 'Neue Anfrage über die Website: ' . $schadensart;

$bodyLines = [
    'Neue Anfrage über das Kontaktformular',
    '----------------------------------------',
    'Name:        ' . $vorname . ' ' . $nachname,
    'Telefon:     ' . ($telefon ?: '—'),
    'E-Mail:      ' . ($email ?: '—'),
    'Schadenort:  ' . ($adresse ?: '—'),
    'Schadensart: ' . $schadensart,
    'Kontaktart:  ' . ($kontaktart ?: '—'),
    '',
    'Nachricht:',
    ($nachricht ?: '—'),
];
$body = implode("\r\n", $bodyLines);

$headers = [
    'From: ' . $from,
    'Content-Type: text/plain; charset=UTF-8',
];
if ($mailOk) {
    $headers[] = 'Reply-To: ' . $email; // Nutzer-Mail nur als Reply-To (validiert)
}

$sent = false;
if (empty($config['dev_mode'])) {
    $sent = @mail($to, encodeSubject($subject), $body, implode("\r\n", $headers));
} else {
    // Entwicklungsmodus: KEINE echte Mail senden.
    $sent = true;
}

if (!$sent) {
    // Nur generischer Fehlercode ins Log, keine Inhaltsdaten.
    error_log('SANI contact.php: mail() fehlgeschlagen');
    respond(false, ['_' => 'Ihre Anfrage konnte nicht gesendet werden. Bitte rufen Sie uns an.'], 500);
}

respond(true, [], 200);

// ===========================================================================
// Helfer
// ===========================================================================
function clean(string $v, int $max = 200): string
{
    $v = str_replace(["\r", "\n"], ' ', $v); // CR/LF entfernen (Header-Injection)
    $v = trim($v);
    return mb_substr($v, 0, $max);
}

function countDigits(string $v): int
{
    return preg_match_all('/\d/', $v);
}

function encodeSubject(string $s): string
{
    return '=?UTF-8?B?' . base64_encode($s) . '?=';
}

function rateLimitOk(string $dir, int $seconds): bool
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0';
    $key = $dir . '/sani_rl_' . hash('sha256', $ip);
    $now = time();
    if (is_file($key) && ($now - (int) @file_get_contents($key)) < $seconds) {
        return false;
    }
    @file_put_contents($key, (string) $now);
    return true;
}

/**
 * Antwort: JSON für fetch/JS, Redirect auf Statusseite für No-JS-POST.
 */
function respond(bool $ok, array $errors, int $status): void
{
    http_response_code($status);
    $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
    $wantsJson = stripos($accept, 'application/json') !== false
        || (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') === 'fetch');

    if ($wantsJson) {
        header('Content-Type: application/json; charset=UTF-8');
        echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'errors' => $errors], JSON_UNESCAPED_UNICODE);
    } else {
        $target = $ok ? '/kontakt/?status=ok' : '/kontakt/?status=fehler';
        header('Location: ' . $target, true, 303);
    }
    exit;
}
