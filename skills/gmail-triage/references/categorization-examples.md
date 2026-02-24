# Email Categorization Examples

Training examples for AI categorization logic.

## Advertising

**Pattern:** Marketing emails, promotions, sales, newsletters with commercial intent

Examples:
- From: `marketing@company.com` Subject: `50% OFF - Limited Time!`
- From: `deals@amazon.com` Subject: `Today's Deals: Up to 70% Off`
- From: `newsletter@techcrunch.com` Subject: `TechCrunch Daily Roundup`

Keywords: sale, offer, discount, promo, limited time, deal, shop now

## Family

**Pattern:** Personal correspondence from non-commercial senders

Examples:
- From: `mom@gmail.com` Subject: `Dinner this Sunday?`
- From: `john.smith@outlook.com` Subject: `Re: Weekend plans`
- From: known personal contacts

Keywords: (context-dependent, requires sender recognition)

## Subscriptions

**Pattern:** Automated newsletters, digest emails, notification summaries

Examples:
- From: `noreply@medium.com` Subject: `Your Daily Digest`
- From: `notifications@github.com` Subject: `[username] starred repo`
- From: `updates@linkedin.com` Subject: `You have 5 new connections`

Keywords: digest, weekly update, notification, summary, newsletter

## Receipts

**Pattern:** Purchase confirmations, order updates, invoices

Examples:
- From: `auto-confirm@amazon.com` Subject: `Your Amazon.com order #123`
- From: `receipts@stripe.com` Subject: `Payment Receipt [Stripe]`
- From: `no-reply@aliexpress.com` Subject: `Order Confirmed`

Keywords: order, receipt, invoice, payment, purchase, confirmation, shipped

## 3D Printing

**Pattern:** Notifications from 3D printing platforms

Examples:
- From: `noreply@makerworld.com` Subject: `New model uploaded`
- From: `no-reply@thangs.com` Subject: `Weekly curated models`
- From: `noreply@printables.com` Subject: `Contest winner announced`

Keywords: MakerWorld, Thangs, Printables, Thingiverse, 3D print, filament

## Work/Tech

**Pattern:** Professional tools, development platforms, tech services

Examples:
- From: `noreply@github.com` Subject: `[repo] Pull request #42`
- From: `notifications@gitlab.com` Subject: `Pipeline failed`
- From: `support@docker.com` Subject: `Docker Hub updates`

Keywords: GitHub, GitLab, Docker, API, deployment, repository, code

## Finance

**Pattern:** Banking, billing, payment notices

Examples:
- From: `alerts@bankofamerica.com` Subject: `Account Alert`
- From: `billing@netflix.com` Subject: `Your payment was processed`
- From: `noreply@paypal.com` Subject: `You sent a payment`

Keywords: bank, payment, bill, due, balance, transaction, account

## Events

**Pattern:** Calendar invitations, appointment reminders, meeting notices

Examples:
- From: `calendar-notification@google.com` Subject: `Event reminder: Dentist`
- From: `appointments@clinic.com` Subject: `Appointment confirmed`
- From: `no-reply@zoom.us` Subject: `Meeting starting soon`

Keywords: appointment, meeting, reminder, calendar, event, RSVP, confirmed

## Action Required

**Pattern:** Emails requiring response or follow-up

Examples:
- Subject contains: `Action required`, `Please respond`, `Awaiting reply`
- From trusted senders asking questions
- Emails with pending tasks or decisions

Keywords: action required, urgent, please respond, waiting for, deadline

## Junk

**Pattern:** Spam, phishing, unwanted marketing (high confidence only)

Examples:
- From: suspicious domains with typos
- Subject: `You won $1,000,000!`, `Enlarge your...`
- Obvious phishing attempts

Keywords: won prize, click here now, suspicious links, Nigerian prince

**Warning:** Only use with 95%+ confidence to avoid false positives
