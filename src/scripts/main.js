/* SANI Trocknung – minimales Frontend-JS (Progressive Enhancement).
   Alles funktioniert ohne JS; dieses Skript ergänzt Komfort/Interaktion. */
(function () {
  'use strict';

  var root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- Sticky-Header: Kompaktierung nach Scroll --------------------------- */
  var header = document.querySelector('[data-header]');
  if (header) {
    var onScroll = function () {
      header.dataset.compact = window.scrollY > 24 ? 'true' : 'false';
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --- Desktop-Dropdown (Leistungen) ------------------------------------- */
  document.querySelectorAll('[data-dropdown]').forEach(function (dd) {
    var toggle = dd.querySelector('[data-dropdown-toggle]');
    if (!toggle) return;
    var close = function () {
      dd.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    };
    var open = function () {
      dd.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
    };
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      dd.classList.contains('is-open') ? close() : open();
    });
    dd.addEventListener('mouseenter', open);
    dd.addEventListener('mouseleave', close);
    dd.addEventListener('focusout', function (e) {
      if (!dd.contains(e.relatedTarget)) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        close();
        toggle.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (!dd.contains(e.target)) close();
    });
  });

  /* --- Mobile-Overlay mit Fokus-Falle ------------------------------------ */
  var mobileNav = document.querySelector('[data-mobile-nav]');
  var openBtn = document.querySelector('[data-menu-open]');
  var lastFocus = null;

  function trapFocus(e) {
    if (e.key !== 'Tab' || !mobileNav || mobileNav.hidden) return;
    var focusables = mobileNav.querySelectorAll(
      'a[href], button:not([disabled]), summary, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusables.length) return;
    var first = focusables[0];
    var last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openMenu() {
    if (!mobileNav) return;
    lastFocus = document.activeElement;
    mobileNav.hidden = false;
    requestAnimationFrame(function () {
      mobileNav.classList.add('is-open');
    });
    if (openBtn) openBtn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    var firstLink = mobileNav.querySelector('a, button');
    if (firstLink) firstLink.focus();
    document.addEventListener('keydown', trapFocus);
  }

  function closeMenu() {
    if (!mobileNav) return;
    mobileNav.classList.remove('is-open');
    if (openBtn) openBtn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    document.removeEventListener('keydown', trapFocus);
    var finish = function () {
      mobileNav.hidden = true;
      if (lastFocus) lastFocus.focus();
    };
    reduceMotion ? finish() : setTimeout(finish, 260);
  }

  if (openBtn) openBtn.addEventListener('click', openMenu);
  document.querySelectorAll('[data-menu-close]').forEach(function (el) {
    el.addEventListener('click', closeMenu);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileNav && !mobileNav.hidden) closeMenu();
  });

  /* --- Akkordeon (FAQ) ---------------------------------------------------- */
  document.querySelectorAll('[data-accordion]').forEach(function (acc) {
    acc.querySelectorAll('.accordion__trigger').forEach(function (trigger) {
      var panel = document.getElementById(trigger.getAttribute('aria-controls'));
      if (!panel) return;
      panel.dataset.open = 'false';
      trigger.setAttribute('aria-expanded', 'false');
      trigger.addEventListener('click', function () {
        var isOpen = trigger.getAttribute('aria-expanded') === 'true';
        trigger.setAttribute('aria-expanded', String(!isOpen));
        panel.dataset.open = String(!isOpen);
      });
    });
  });

  /* --- Reveal-Observer ---------------------------------------------------- */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    document.querySelectorAll('.reveal, .reveal-stagger').forEach(function (el) {
      io.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal, .reveal-stagger').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /* --- Sticky-Aktionsleiste: auf /kontakt ab Formular ausblenden --------- */
  var stickybar = document.querySelector('[data-stickybar]');
  var formAnchor = document.getElementById('formular');
  if (stickybar && formAnchor && 'IntersectionObserver' in window) {
    var sbObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          stickybar.dataset.hidden = entry.isIntersecting ? 'true' : 'false';
        });
      },
      { threshold: 0.05 }
    );
    sbObserver.observe(formAnchor);
  }

  /* --- Parallax (transform-only, scroll-linked, kein Scroll-Jacking) ----- */
  if (!reduceMotion) {
    var parallaxEls = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
    if (parallaxEls.length) {
      var rafId = null;
      var updateParallax = function () {
        var vh = window.innerHeight;
        parallaxEls.forEach(function (el) {
          var rect = el.getBoundingClientRect();
          if (rect.bottom < -200 || rect.top > vh + 200) return; // nur nahe am Viewport
          var speed = parseFloat(el.getAttribute('data-parallax')) || 0.12;
          var center = rect.top + rect.height / 2 - vh / 2;
          el.style.transform = 'translate3d(0,' + (center * speed * -1).toFixed(1) + 'px,0)';
        });
        rafId = null;
      };
      var queueParallax = function () {
        if (rafId === null) rafId = requestAnimationFrame(updateParallax);
      };
      window.addEventListener('scroll', queueParallax, { passive: true });
      window.addEventListener('resize', queueParallax);
      updateParallax();
    }
  }

  /* --- Vorher/Nachher-Regler (Wiederherstellung) -------------------------
     Native <input type="range">: per Maus, Touch, Tastatur bedienbar.
     Beim ersten Sichtbarwerden fährt der Regler einmalig auf 55% (Reveal);
     die CSS-Transition dafür entfällt automatisch unter reduced-motion. --- */
  document.querySelectorAll('[data-compare]').forEach(function (compare) {
    var range = compare.querySelector('[data-compare-range]');
    var frame = compare.querySelector('.compare__frame');
    if (!range || !frame) return;
    var setPos = function (v) {
      frame.style.setProperty('--compare-pos', v + '%');
    };
    setPos(range.value);
    range.addEventListener('input', function () {
      setPos(range.value);
    });
    if ('IntersectionObserver' in window) {
      var revealed = false;
      var cio = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting && !revealed) {
              revealed = true;
              range.value = '55';
              setPos(55);
              cio.unobserve(compare);
            }
          });
        },
        { threshold: 0.35 }
      );
      cio.observe(compare);
    } else {
      range.value = '55';
      setPos(55);
    }
  });

  /* --- Formular-UX (nur ergänzend, native Validierung bleibt Fallback) --- */
  var form = document.querySelector('[data-contact-form]');
  if (form) initContactForm(form);

  function initContactForm(form) {
    var summary = form.querySelector('[data-form-summary]');
    var submitBtn = form.querySelector('[data-submit]');
    var submitted = false;

    function setFieldError(field, message) {
      var wrap = field.closest('.form-field, .checkbox-field');
      if (!wrap) return;
      var errEl = wrap.querySelector('.field-error');
      wrap.dataset.error = message ? 'true' : 'false';
      if (errEl) errEl.textContent = message || '';
      field.setAttribute('aria-invalid', message ? 'true' : 'false');
    }

    function validEmail(v) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    }
    function validPhone(v) {
      var digits = (v.match(/\d/g) || []).length;
      return /^[+\d][\d\s/()-]*$/.test(v) && digits >= 6 && digits <= 20;
    }

    function validate() {
      var errors = [];
      var f = form.elements;

      ['vorname', 'nachname'].forEach(function (n) {
        var el = f[n];
        if (!el) return;
        var v = el.value.trim();
        if (v.length < 2 || v.length > 60) {
          setFieldError(el, 'Bitte geben Sie Ihren ' + (n === 'vorname' ? 'Vornamen' : 'Nachnamen') + ' ein.');
          errors.push(el);
        } else setFieldError(el, '');
      });

      var tel = f['telefon'];
      var mail = f['email'];
      var telVal = tel ? tel.value.trim() : '';
      var mailVal = mail ? mail.value.trim() : '';
      var telOk = telVal === '' || validPhone(telVal);
      var mailOk = mailVal === '' || validEmail(mailVal);
      if (telVal && !telOk) {
        setFieldError(tel, 'Bitte geben Sie eine gültige Telefonnummer ein.');
        errors.push(tel);
      } else setFieldError(tel, '');
      if (mailVal && !mailOk) {
        setFieldError(mail, 'Bitte geben Sie eine gültige E-Mail-Adresse ein (z. B. name@beispiel.de).');
        errors.push(mail);
      } else if (mailOk) setFieldError(mail, '');
      if (!telVal && !mailVal) {
        setFieldError(tel, 'Bitte geben Sie Telefonnummer oder E-Mail-Adresse an.');
        setFieldError(mail, 'Bitte geben Sie Telefonnummer oder E-Mail-Adresse an.');
        errors.push(tel);
      }

      var art = f['schadensart'];
      if (art && !art.value) {
        setFieldError(art, 'Bitte wählen Sie die Art des Schadens aus.');
        errors.push(art);
      } else if (art) setFieldError(art, '');

      var dsgvo = f['datenschutz'];
      if (dsgvo && !dsgvo.checked) {
        setFieldError(dsgvo, 'Bitte bestätigen Sie die Datenschutzerklärung.');
        errors.push(dsgvo);
      } else if (dsgvo) setFieldError(dsgvo, '');

      return errors;
    }

    form.addEventListener('submit', function (e) {
      submitted = true;
      var errors = validate();
      if (errors.length) {
        e.preventDefault();
        if (summary) {
          summary.hidden = false;
          summary.textContent =
            'Bitte prüfen Sie die markierten Felder – Ihre Anfrage wurde noch nicht gesendet.';
          summary.focus();
        }
        return;
      }
      if (summary) summary.hidden = true;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.label = submitBtn.textContent;
        submitBtn.textContent = 'Wird gesendet…';
      }
      // Kein Live-Endpoint aktiv (PH-08): natives Submit erfolgt an formEndpoint,
      // solange nicht produktiv geschaltet, bleibt dies eine reine UX-Demonstration.
    });

    // Inline-Revalidierung erst nach dem ersten Absenden (kein Sofort-Rot).
    form.addEventListener('input', function (e) {
      if (submitted && e.target && e.target.name) validate();
    });
  }
})();
