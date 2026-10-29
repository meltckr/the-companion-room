import Foundation
import LinkPresentation

let provider = LPMetadataProvider()
provider.timeout = 35
let target = URL(string: "https://meltckr.github.io/the-companion-room/?v=4")!
provider.startFetchingMetadata(for: target) { metadata, error in
    if let error = error {
        print("APPLE_PREVIEW_ERROR: \(error.localizedDescription)")
        exit(1)
    }
    guard let metadata = metadata else {
        print("APPLE_PREVIEW_ERROR: No metadata returned")
        exit(1)
    }
    print("APPLE_PREVIEW_TITLE: \(metadata.title ?? "missing")")
    print("APPLE_PREVIEW_URL: \(metadata.url?.absoluteString ?? "missing")")
    print("APPLE_PREVIEW_IMAGE: \(metadata.imageProvider != nil)")
    print("APPLE_PREVIEW_ICON: \(metadata.iconProvider != nil)")
    guard let image = metadata.imageProvider, let type = image.registeredTypeIdentifiers.first else { exit(2) }
    image.loadDataRepresentation(forTypeIdentifier: type) { data, error in
        guard let data = data else {
            print("APPLE_PREVIEW_IMAGE_DATA_ERROR: \(error?.localizedDescription ?? "missing data")")
            exit(2)
        }
        let output = URL(fileURLWithPath: "/Users/meltucker/Documents/Phoenix Suns 2/east-lansing-pet-spa/evidence/realism/apple-preview-image")
        do {
            try data.write(to: output)
            print("APPLE_PREVIEW_IMAGE_BYTES: \(data.count)")
            exit(0)
        } catch {
            print("APPLE_PREVIEW_WRITE_ERROR: \(error.localizedDescription)")
            exit(2)
        }
    }
}
RunLoop.main.run(until: Date(timeIntervalSinceNow: 45))
print("APPLE_PREVIEW_ERROR: Timed out")
exit(3)
