import { Namespace, SubjectSet, Context } from "@ory/permission-namespace-types"

class User implements Namespace { }

class Internal implements Namespace {
  related: {
    admins: User[]
    users: User[]
  }

  permits = {
    //only admins can view/edit users (could also change read/write to something like viewUsers, updateUsers, etc)
    read: (ctx: Context): boolean => this.permits.write(ctx),
    write: (ctx: Context): boolean => this.related.admins.includes(ctx.subject),
    // booking actions
    viewBookings: (ctx: Context): boolean => this.related.users.includes(ctx.subject) || this.permits.write(ctx),
  }
}
