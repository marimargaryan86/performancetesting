import { Namespace, SubjectSet, Context } from "@ory/permission-namespace-types"

class User implements Namespace { }

class Group implements Namespace {
  related: {
    admins: User[]
    members: User[]
  }

  permits = {
    metaWrite: (ctx: Context) => this.related.admins.includes(ctx.subject),
    // you can read when you can write, or when you are a "normal" member
    metaRead: (ctx: Context) => this.permits.metaWrite(ctx) || this.related.members.includes(ctx.subject),
    // new booking will have its own permissions, but because it is associated with a group we check the permission here
    createNewBooking: (ctx: Context) => this.related.admins.includes(ctx.subject)
  }
}

class Booking implements Namespace {
  related: {
    admins: User[]
    members: User[]
  }

  permits = {
    metaWrite: (ctx: Context) => this.related.admins.includes(ctx.subject),
    // you can read when you can write, or when you are a "normal" member
    metaRead: (ctx: Context) => this.permits.metaWrite(ctx) || this.related.members.includes(ctx.subject),
  }
}

class NewRefund implements Namespace {
  // this namespace is only instantiated once to check whether a new refund can be created
  // the only instance will then be related to all users or groups that have the ability to create refunds

  related: {
    specialUsers: User[]
    specialGroups: Group[]
  }

  permits = {
    createNew: (ctx: Context) => this.related.specialUsers.includes(ctx.subject) ||
      this.related.specialGroups.traverse(group => group.related.admins.includes(ctx.subject))
  }
}

class Refund implements Namespace {
  related: {
  }

  permits = {
  }
}
