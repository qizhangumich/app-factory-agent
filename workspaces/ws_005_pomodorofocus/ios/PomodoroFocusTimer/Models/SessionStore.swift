//
//  SessionStore.swift
//  PomodoroFocusTimer
//
//  Core Data persistence.
//
//  DESIGN DECISION: spec.data_storage requires Core Data on iOS, but the
//  target is iOS 16 (so SwiftData is unavailable) and a hand-authored
//  binary `.xcdatamodeld` is fragile to produce off-device. We therefore
//  build the `NSManagedObjectModel` ENTIRELY IN CODE here. No `.xcdatamodeld`
//  file is needed and the schema cannot drift from a binary blob.
//

import CoreData
import Combine

/// A managed object backing one Pomodoro session.
@objc(SessionEntity)
final class SessionEntity: NSManagedObject {
    @NSManaged var id: UUID
    @NSManaged var date: Date
    @NSManaged var type: String
    @NSManaged var durationSeconds: Int64
    @NSManaged var completedAt: Date
}

extension SessionEntity {
    /// The entity name used throughout the store.
    static let entityName = "SessionEntity"

    /// Builds the `NSManagedObjectModel` programmatically.
    static func makeModel() -> NSManagedObjectModel {
        let entity = NSEntityDescription()
        entity.name = entityName
        entity.managedObjectClassName = NSStringFromClass(SessionEntity.self)

        func attr(_ name: String,
                  _ type: NSAttributeType,
                  optional: Bool = false) -> NSAttributeDescription {
            let a = NSAttributeDescription()
            a.name = name
            a.attributeType = type
            a.isOptional = optional
            return a
        }

        entity.properties = [
            attr("id", .UUIDAttributeType),
            attr("date", .dateAttributeType),
            attr("type", .stringAttributeType),
            attr("durationSeconds", .integer64AttributeType),
            attr("completedAt", .dateAttributeType)
        ]

        let model = NSManagedObjectModel()
        model.entities = [entity]
        return model
    }

    /// Maps the managed object to the immutable `Session` value type.
    var asSession: Session {
        Session(id: id,
                date: date,
                type: PomodoroPhase(rawValue: type) ?? .focus,
                durationSeconds: Int(durationSeconds),
                completedAt: completedAt)
    }
}

/// Owns the Core Data stack and exposes session CRUD + stats queries.
final class SessionStore: ObservableObject {
    static let shared = SessionStore()

    /// All sessions, newest first. Published so views refresh on change.
    @Published private(set) var sessions: [Session] = []

    private let container: NSPersistentContainer

    private init(inMemory: Bool = false) {
        let model = SessionEntity.makeModel()
        container = NSPersistentContainer(name: "PomodoroFocus", managedObjectModel: model)

        if inMemory {
            container.persistentStoreDescriptions.first?.url =
                URL(fileURLWithPath: "/dev/null")
        }
        container.loadPersistentStores { _, error in
            if let error = error {
                // A store-load failure is non-recoverable; surface it loudly in debug.
                assertionFailure("Core Data store failed to load: \(error)")
            }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        reload()
    }

    private var context: NSManagedObjectContext { container.viewContext }

    // MARK: - Mutations

    /// Records a finished session.
    func add(type: PomodoroPhase, durationSeconds: Int, completedAt: Date = Date()) {
        let entity = SessionEntity(context: context)
        entity.id = UUID()
        entity.date = Calendar.current.startOfDay(for: completedAt)
        entity.type = type.rawValue
        entity.durationSeconds = Int64(durationSeconds)
        entity.completedAt = completedAt
        save()
    }

    /// Removes every stored session (used by the "reset statistics" action).
    func deleteAll() {
        let request: NSFetchRequest<NSFetchRequestResult> =
            NSFetchRequest(entityName: SessionEntity.entityName)
        let delete = NSBatchDeleteRequest(fetchRequest: request)
        delete.resultType = .resultTypeObjectIDs
        do {
            let result = try context.execute(delete) as? NSBatchDeleteResult
            if let ids = result?.result as? [NSManagedObjectID] {
                NSManagedObjectContext.mergeChanges(
                    fromRemoteContextSave: [NSDeletedObjectsKey: ids],
                    into: [context])
            }
        } catch {
            assertionFailure("Batch delete failed: \(error)")
        }
        reload()
    }

    private func save() {
        guard context.hasChanges else { return }
        do {
            try context.save()
            reload()
        } catch {
            assertionFailure("Core Data save failed: \(error)")
        }
    }

    /// Refreshes the published `sessions` array from the store.
    func reload() {
        let request = NSFetchRequest<SessionEntity>(entityName: SessionEntity.entityName)
        request.sortDescriptors = [NSSortDescriptor(key: "completedAt", ascending: false)]
        do {
            sessions = try context.fetch(request).map(\.asSession)
        } catch {
            sessions = []
            assertionFailure("Core Data fetch failed: \(error)")
        }
    }
}
