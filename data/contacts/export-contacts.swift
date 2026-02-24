#!/usr/bin/swift
import Contacts
import Foundation

let store = CNContactStore()

// Request access
let semaphore = DispatchSemaphore(value: 0)
var accessGranted = false

store.requestAccess(for: .contacts) { granted, error in
    accessGranted = granted
    if let error = error {
        print("Error requesting access: \(error.localizedDescription)", to: &standardError)
    }
    semaphore.signal()
}

semaphore.wait()

guard accessGranted else {
    print("Access to contacts denied", to: &standardError)
    exit(1)
}

// Define keys to fetch
let keysToFetch = [
    CNContactGivenNameKey,
    CNContactFamilyNameKey,
    CNContactEmailAddressesKey,
    CNContactPhoneNumbersKey,
    CNContactDatesKey
] as [CNKeyDescriptor]

// Fetch all contacts
let fetchRequest = CNContactFetchRequest(keysToFetch: keysToFetch)
fetchRequest.unifyResults = true

var contacts: [CNContact] = []

do {
    try store.enumerateContacts(with: fetchRequest) { contact, stop in
        contacts.append(contact)
    }
} catch {
    print("Error fetching contacts: \(error.localizedDescription)", to: &standardError)
    exit(1)
}

// Print TSV header
print("Name\tPhone\tEmail\tLastModified")

// Print contacts
for contact in contacts {
    let name = "\(contact.givenName) \(contact.familyName)".trimmingCharacters(in: .whitespaces)
    
    let phones = contact.phoneNumbers
        .map { $0.value.stringValue }
        .joined(separator: ", ")
    
    let emails = contact.emailAddresses
        .map { $0.value as String }
        .joined(separator: ", ")
    
    // Note: CNContact doesn't directly expose modification date
    // We'll leave it empty for now
    let lastModified = ""
    
    print("\(name)\t\(phones)\t\(emails)\t\(lastModified)")
}

// Print count to stderr
print("Total contacts exported: \(contacts.count)", to: &standardError)

var standardError = FileHandle.standardError

extension FileHandle: TextOutputStream {
    public func write(_ string: String) {
        guard let data = string.data(using: .utf8) else { return }
        self.write(data)
    }
}
